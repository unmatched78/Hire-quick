from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import json
import sys
import os
from django.conf import settings

# Add scripts directory to path
sys.path.append(os.path.join(settings.BASE_DIR, 'scripts'))
from job_matching_engine import JobMatchingEngine

from .models import TalentPool, TalentPoolCandidate, JobMatch, CandidatePreferences, MatchingActivity
from .forms import TalentPoolForm, TalentPoolCandidateForm, CandidatePreferencesForm
from accounts.models import CandidateProfile, RecruiterProfile
from jobs.models import Job
from applications.models import ParsedResume

class TalentPoolListView(LoginRequiredMixin, ListView):
    model = TalentPool
    template_name = 'talent_pool/pool_list.html'
    context_object_name = 'talent_pools'
    paginate_by = 12
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can access talent pools.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = TalentPool.objects.filter(
            company=self.request.user.recruiter_profile.company
        ).annotate(
            candidate_count=Count('candidates'),
            recent_additions=Count('candidates', filter=Q(candidates__added_at__gte=timezone.now() - timedelta(days=7)))
        )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by pool type
        pool_type = self.request.GET.get('pool_type')
        if pool_type:
            queryset = queryset.filter(pool_type=pool_type)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')

class TalentPoolDetailView(LoginRequiredMixin, DetailView):
    model = TalentPool
    template_name = 'talent_pool/pool_detail.html'
    context_object_name = 'talent_pool'
    
    def dispatch(self, request, *args, **kwargs):
        pool = self.get_object()
        if request.user.user_type != 'recruiter' or pool.company != request.user.recruiter_profile.company:
            messages.error(request, 'You can only view your company\'s talent pools.')
            return redirect('talent_pool:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get candidates with pagination
        candidates = self.object.candidates.select_related('candidate', 'candidate__user').order_by('-match_score', '-added_at')
        
        # Filter candidates
        status_filter = self.request.GET.get('status')
        if status_filter:
            candidates = candidates.filter(status=status_filter)
        
        priority_filter = self.request.GET.get('priority')
        if priority_filter:
            candidates = candidates.filter(priority=priority_filter)
        
        search = self.request.GET.get('search')
        if search:
            candidates = candidates.filter(
                Q(candidate__first_name__icontains=search) |
                Q(candidate__last_name__icontains=search) |
                Q(candidate__user__email__icontains=search)
            )
        
        paginator = Paginator(candidates, 20)
        page_number = self.request.GET.get('page')
        context['candidates'] = paginator.get_page(page_number)
        
        # Statistics
        context['stats'] = {
            'total_candidates': self.object.candidates.count(),
            'active_candidates': self.object.candidates.filter(status='active').count(),
            'contacted_candidates': self.object.candidates.filter(status='contacted').count(),
            'interested_candidates': self.object.candidates.filter(status='interested').count(),
            'avg_match_score': self.object.candidates.aggregate(avg_score=Avg('match_score'))['avg_score'] or 0,
        }
        
        return context

class TalentPoolCreateView(LoginRequiredMixin, CreateView):
    model = TalentPool
    form_class = TalentPoolForm
    template_name = 'talent_pool/pool_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can create talent pools.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.company = self.request.user.recruiter_profile.company
        form.instance.created_by = self.request.user.recruiter_profile
        messages.success(self.request, 'Talent pool created successfully!')
        return super().form_valid(form)

@login_required
def add_candidate_to_pool(request, pool_id):
    """Add a candidate to a talent pool"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can manage talent pools.')
        return redirect('dashboard:home')
    
    pool = get_object_or_404(TalentPool, pk=pool_id, company=request.user.recruiter_profile.company)
    
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
        
        # Check if candidate is already in pool
        if TalentPoolCandidate.objects.filter(talent_pool=pool, candidate=candidate).exists():
            messages.warning(request, 'Candidate is already in this talent pool.')
        else:
            # Calculate match score
            engine = JobMatchingEngine()
            
            # Prepare candidate data
            candidate_data = {
                'skills': candidate.skills or [],
                'total_experience_years': candidate.experience_years,
                'location': candidate.location,
                'education': [],  # Would need to be populated from parsed resume
                'preferences': {}
            }
            
            # Prepare pool criteria as job data
            pool_data = {
                'required_skills': pool.required_skills,
                'preferred_skills': pool.preferred_skills,
                'min_experience': pool.min_experience,
                'max_experience': pool.max_experience,
                'location': pool.locations[0] if pool.locations else '',
                'remote_ok': 'remote' in [loc.lower() for loc in pool.locations] if pool.locations else False
            }
            
            match_result = engine.calculate_comprehensive_match(candidate_data, pool_data)
            
            # Add candidate to pool
            pool_candidate = TalentPoolCandidate.objects.create(
                talent_pool=pool,
                candidate=candidate,
                added_by=request.user.recruiter_profile,
                match_score=match_result['overall_score'],
                matched_skills=match_result['matched_skills'],
                missing_skills=match_result['missing_skills']
            )
            
            # Log activity
            MatchingActivity.objects.create(
                candidate=candidate,
                talent_pool=pool,
                action='pool_added',
                details={'match_score': match_result['overall_score']}
            )
            
            messages.success(request, f'Candidate added to {pool.name} with {match_result["overall_score"]}% match.')
        
        return redirect('talent_pool:detail', pk=pool_id)
    
    # Get available candidates (not already in pool)
    existing_candidate_ids = pool.candidates.values_list('candidate_id', flat=True)
    available_candidates = CandidateProfile.objects.exclude(
        id__in=existing_candidate_ids
    ).select_related('user')[:50]  # Limit for performance
    
    return render(request, 'talent_pool/add_candidate.html', {
        'pool': pool,
        'available_candidates': available_candidates
    })

@login_required
def candidate_job_matches(request):
    """View personalized job matches for candidate"""
    if request.user.user_type != 'candidate':
        messages.error(request, 'Only candidates can view job matches.')
        return redirect('dashboard:home')
    
    candidate_profile = request.user.candidate_profile
    
    # Get or create preferences
    preferences, created = CandidatePreferences.objects.get_or_create(candidate=candidate_profile)
    
    # Get job matches
    matches = JobMatch.objects.filter(candidate=candidate_profile).select_related('job', 'job__company').order_by('-overall_score')
    
    # Filter matches
    status_filter = request.GET.get('status')
    if status_filter:
        matches = matches.filter(status=status_filter)
    
    min_score = request.GET.get('min_score')
    if min_score:
        try:
            matches = matches.filter(overall_score__gte=float(min_score))
        except ValueError:
            pass
    
    paginator = Paginator(matches, 10)
    page_number = request.GET.get('page')
    matches_page = paginator.get_page(page_number)
    
    return render(request, 'talent_pool/candidate_matches.html', {
        'matches': matches_page,
        'preferences': preferences,
        'stats': {
            'total_matches': matches.count(),
            'pending_matches': matches.filter(status='pending').count(),
            'viewed_matches': matches.filter(status='viewed').count(),
            'applied_matches': matches.filter(status='applied').count(),
        }
    })

@login_required
def update_candidate_preferences(request):
    """Update candidate job preferences"""
    if request.user.user_type != 'candidate':
        messages.error(request, 'Only candidates can update preferences.')
        return redirect('dashboard:home')
    
    candidate_profile = request.user.candidate_profile
    preferences, created = CandidatePreferences.objects.get_or_create(candidate=candidate_profile)
    
    if request.method == 'POST':
        form = CandidatePreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            
            # Log activity
            MatchingActivity.objects.create(
                candidate=candidate_profile,
                action='preferences_updated'
            )
            
            messages.success(request, 'Preferences updated successfully!')
            return redirect('talent_pool:candidate_matches')
    else:
        form = CandidatePreferencesForm(instance=preferences)
    
    return render(request, 'talent_pool/update_preferences.html', {
        'form': form,
        'preferences': preferences
    })

@login_required
@require_POST
def generate_job_matches(request):
    """Generate new job matches for all candidates"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        engine = JobMatchingEngine()
        
        # Get active jobs from recruiter's company
        jobs = Job.objects.filter(
            company=request.user.recruiter_profile.company,
            status='active'
        )
        
        # Get all candidates with parsed resumes
        candidates = CandidateProfile.objects.filter(
            applications__parsed_resume__isnull=False
        ).distinct()
        
        matches_created = 0
        
        for job in jobs:
            # Prepare job data
            job_data = {
                'title': job.title,
                'required_skills': job.requirements or [],
                'preferred_skills': job.preferred_skills or [],
                'min_experience': job.experience_min,
                'max_experience': job.experience_max,
                'location': job.location,
                'remote_ok': job.remote_ok,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'job_type': job.job_type,
                'education_required': job.education_required
            }
            
            for candidate in candidates:
                # Skip if match already exists
                if JobMatch.objects.filter(candidate=candidate, job=job).exists():
                    continue
                
                # Get parsed resume data
                try:
                    parsed_resume = candidate.applications.filter(
                        parsed_resume__isnull=False
                    ).first().parsed_resume
                    
                    candidate_data = {
                        'skills': parsed_resume.get_all_skills(),
                        'total_experience_years': parsed_resume.total_experience_years,
                        'location': candidate.location,
                        'education': parsed_resume.education_data,
                        'preferences': {}
                    }
                    
                    # Get preferences if available
                    if hasattr(candidate, 'job_preferences'):
                        prefs = candidate.job_preferences
                        candidate_data['preferences'] = {
                            'job_types': prefs.job_types,
                            'min_salary': prefs.min_salary,
                            'max_salary': prefs.max_salary,
                            'remote_preference': prefs.remote_preference
                        }
                    
                    # Calculate match
                    match_result = engine.calculate_comprehensive_match(candidate_data, job_data)
                    
                    # Only create match if score is above threshold
                    if match_result['overall_score'] >= 50:
                        JobMatch.objects.create(
                            candidate=candidate,
                            job=job,
                            match_type='auto',
                            overall_score=match_result['overall_score'],
                            skill_score=match_result['skill_score'],
                            experience_score=match_result['experience_score'],
                            location_score=match_result['location_score'],
                            education_score=match_result['education_score'],
                            matched_skills=match_result['matched_skills'],
                            missing_skills=match_result['missing_skills'],
                            match_reasons=match_result['match_reasons'],
                            ai_recommendation=match_result['ai_recommendation'],
                            fit_analysis=match_result['fit_analysis'],
                            expires_at=timezone.now() + timedelta(days=30)
                        )
                        
                        matches_created += 1
                        
                        # Log activity
                        MatchingActivity.objects.create(
                            candidate=candidate,
                            job=job,
                            action='match_created',
                            details={'match_score': match_result['overall_score']}
                        )
                
                except Exception as e:
                    print(f"Error processing candidate {candidate.id}: {e}")
                    continue
        
        return JsonResponse({
            'success': True,
            'matches_created': matches_created,
            'message': f'Generated {matches_created} new job matches'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def job_match_detail(request, pk):
    """View detailed job match information"""
    match = get_object_or_404(JobMatch, pk=pk)
    
    # Check permissions
    if request.user.user_type == 'candidate':
        if match.candidate.user != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('talent_pool:candidate_matches')
        
        # Mark as viewed
        if match.status == 'pending':
            match.status = 'viewed'
            match.viewed_at = timezone.now()
            match.save()
            
            # Log activity
            MatchingActivity.objects.create(
                candidate=match.candidate,
                job=match.job,
                action='match_viewed'
            )
    
    elif request.user.user_type == 'recruiter':
        if match.job.recruiter != request.user.recruiter_profile:
            messages.error(request, 'Permission denied.')
            return redirect('talent_pool:list')
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:home')
    
    return render(request, 'talent_pool/job_match_detail.html', {
        'match': match
    })

@login_required
@require_POST
def update_match_status(request, pk):
    """Update job match status"""
    match = get_object_or_404(JobMatch, pk=pk)
    
    if request.user.user_type == 'candidate' and match.candidate.user == request.user:
        new_status = request.POST.get('status')
        if new_status in dict(JobMatch.STATUS_CHOICES):
            old_status = match.status
            match.status = new_status
            match.responded_at = timezone.now()
            match.save()
            
            # Log activity
            MatchingActivity.objects.create(
                candidate=match.candidate,
                job=match.job,
                action=f'match_{new_status}',
                details={'previous_status': old_status}
            )
            
            messages.success(request, f'Match status updated to {match.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    else:
        messages.error(request, 'Permission denied')
    
    return redirect('talent_pool:job_match_detail', pk=pk)

@login_required
def matching_analytics(request):
    """View matching analytics dashboard"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view analytics.')
        return redirect('dashboard:home')
    
    company = request.user.recruiter_profile.company
    
    # Get analytics data
    total_matches = JobMatch.objects.filter(job__company=company).count()
    recent_matches = JobMatch.objects.filter(
        job__company=company,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Match status distribution
    status_distribution = {}
    for status, _ in JobMatch.STATUS_CHOICES:
        count = JobMatch.objects.filter(job__company=company, status=status).count()
        status_distribution[status] = count
    
    # Top performing jobs
    top_jobs = Job.objects.filter(company=company).annotate(
        match_count=Count('candidate_matches')
    ).order_by('-match_count')[:10]
    
    # Average match scores
    avg_scores = JobMatch.objects.filter(job__company=company).aggregate(
        avg_overall=Avg('overall_score'),
        avg_skill=Avg('skill_score'),
        avg_experience=Avg('experience_score'),
        avg_location=Avg('location_score')
    )
    
    return render(request, 'talent_pool/matching_analytics.html', {
        'total_matches': total_matches,
        'recent_matches': recent_matches,
        'status_distribution': status_distribution,
        'top_jobs': top_jobs,
        'avg_scores': avg_scores
    })

class TalentPoolUpdateView(LoginRequiredMixin, UpdateView):
    model = TalentPool
    form_class = TalentPoolForm
    template_name = 'talent_pool/pool_edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        pool = self.get_object()
        if request.user.user_type != 'recruiter' or pool.company != request.user.recruiter_profile.company:
            messages.error(request, 'You can only edit your company\'s talent pools.')
            return redirect('talent_pool:list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Talent pool updated successfully!')
        return super().form_valid(form)

class TalentPoolDeleteView(LoginRequiredMixin, DeleteView):
    model = TalentPool
    template_name = 'talent_pool/pool_confirm_delete.html'
    success_url = reverse_lazy('talent_pool:list')
    
    def dispatch(self, request, *args, **kwargs):
        pool = self.get_object()
        if request.user.user_type != 'recruiter' or pool.company != request.user.recruiter_profile.company:
            messages.error(request, 'You can only delete your company\'s talent pools.')
            return redirect('talent_pool:list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Talent pool deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def remove_candidate_from_pool(request, candidate_id, pool_id):
    """Remove a candidate from a talent pool"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    pool = get_object_or_404(TalentPool, pk=pool_id, company=request.user.recruiter_profile.company)
    candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
    
    try:
        pool_candidate = TalentPoolCandidate.objects.get(talent_pool=pool, candidate=candidate)
        pool_candidate.delete()
        
        # Log activity
        MatchingActivity.objects.create(
            candidate=candidate,
            talent_pool=pool,
            action='pool_removed'
        )
        
        return JsonResponse({'success': True, 'message': 'Candidate removed from pool'})
    except TalentPoolCandidate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Candidate not in pool'})

@login_required
def update_pool_candidate(request, pk):
    """Update talent pool candidate status and notes"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Permission denied.')
        return redirect('talent_pool:list')
    
    pool_candidate = get_object_or_404(
        TalentPoolCandidate, 
        pk=pk,
        talent_pool__company=request.user.recruiter_profile.company
    )
    
    if request.method == 'POST':
        form = TalentPoolCandidateForm(request.POST, instance=pool_candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully!')
            return redirect('talent_pool:detail', pk=pool_candidate.talent_pool.pk)
    else:
        form = TalentPoolCandidateForm(instance=pool_candidate)
    
    return render(request, 'talent_pool/update_candidate.html', {
        'form': form,
        'pool_candidate': pool_candidate
    })

@login_required
@require_POST
def bulk_add_candidates(request):
    """Bulk add candidates to talent pools"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        pool_id = request.POST.get('pool_id')
        candidate_ids = request.POST.getlist('candidate_ids')
        
        pool = get_object_or_404(TalentPool, pk=pool_id, company=request.user.recruiter_profile.company)
        
        added_count = 0
        engine = JobMatchingEngine()
        
        for candidate_id in candidate_ids:
            candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
            
            # Skip if already in pool
            if TalentPoolCandidate.objects.filter(talent_pool=pool, candidate=candidate).exists():
                continue
            
            # Calculate match score
            candidate_data = {
                'skills': candidate.skills or [],
                'total_experience_years': candidate.experience_years,
                'location': candidate.location,
                'education': [],
                'preferences': {}
            }
            
            pool_data = {
                'required_skills': pool.required_skills,
                'preferred_skills': pool.preferred_skills,
                'min_experience': pool.min_experience,
                'max_experience': pool.max_experience,
                'location': pool.locations[0] if pool.locations else '',
                'remote_ok': 'remote' in [loc.lower() for loc in pool.locations] if pool.locations else False
            }
            
            match_result = engine.calculate_comprehensive_match(candidate_data, pool_data)
            
            # Add to pool
            TalentPoolCandidate.objects.create(
                talent_pool=pool,
                candidate=candidate,
                added_by=request.user.recruiter_profile,
                match_score=match_result['overall_score'],
                matched_skills=match_result['matched_skills'],
                missing_skills=match_result['missing_skills']
            )
            
            added_count += 1
        
        return JsonResponse({
            'success': True,
            'added_count': added_count,
            'message': f'Successfully added {added_count} candidates to {pool.name}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def pool_analytics(request, pk):
    """Detailed analytics for a specific talent pool"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view analytics.')
        return redirect('dashboard:home')
    
    pool = get_object_or_404(TalentPool, pk=pk, company=request.user.recruiter_profile.company)
    
    # Pool statistics
    candidates = pool.candidates.all()
    total_candidates = candidates.count()
    
    # Status distribution
    status_distribution = {}
    for status, _ in TalentPoolCandidate.STATUS_CHOICES:
        count = candidates.filter(status=status).count()
        status_distribution[status] = count
    
    # Match score distribution
    score_ranges = {
        '90-100%': candidates.filter(match_score__gte=90).count(),
        '80-89%': candidates.filter(match_score__gte=80, match_score__lt=90).count(),
        '70-79%': candidates.filter(match_score__gte=70, match_score__lt=80).count(),
        '60-69%': candidates.filter(match_score__gte=60, match_score__lt=70).count(),
        'Below 60%': candidates.filter(match_score__lt=60).count(),
    }
    
    # Top skills analysis
    all_skills = {}
    for candidate in candidates:
        for skill in candidate.matched_skills:
            all_skills[skill] = all_skills.get(skill, 0) + 1
    
    top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Recent activity
    recent_activities = MatchingActivity.objects.filter(
        talent_pool=pool
    ).order_by('-created_at')[:20]
    
    context = {
        'pool': pool,
        'total_candidates': total_candidates,
        'status_distribution': status_distribution,
        'score_ranges': score_ranges,
        'top_skills': top_skills,
        'recent_activities': recent_activities,
        'avg_match_score': candidates.aggregate(avg_score=Avg('match_score'))['avg_score'] or 0,
    }
    
    return render(request, 'talent_pool/pool_analytics.html', context)

@login_required
def search_candidates_api(request):
    """API endpoint for searching candidates"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    query = request.GET.get('q', '')
    pool_id = request.GET.get('pool_id')
    
    candidates = CandidateProfile.objects.select_related('user')
    
    # Exclude candidates already in the pool
    if pool_id:
        existing_candidate_ids = TalentPoolCandidate.objects.filter(
            talent_pool_id=pool_id
        ).values_list('candidate_id', flat=True)
        candidates = candidates.exclude(id__in=existing_candidate_ids)
    
    # Search filter
    if query:
        candidates = candidates.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(current_title__icontains=query)
        )
    
    # Limit results
    candidates = candidates[:20]
    
    results = []
    for candidate in candidates:
        results.append({
            'id': candidate.id,
            'name': candidate.get_full_name(),
            'email': candidate.user.email,
            'title': candidate.current_title or 'No title',
            'location': candidate.location or 'No location',
            'experience_years': candidate.experience_years or 0,
        })
    
    return JsonResponse({'candidates': results})

@login_required
def match_preview_api(request):
    """API endpoint for previewing match scores"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        candidate_id = request.GET.get('candidate_id')
        pool_id = request.GET.get('pool_id')
        
        candidate = get_object_or_404(CandidateProfile, pk=candidate_id)
        pool = get_object_or_404(TalentPool, pk=pool_id, company=request.user.recruiter_profile.company)
        
        # Calculate match
        engine = JobMatchingEngine()
        
        candidate_data = {
            'skills': candidate.skills or [],
            'total_experience_years': candidate.experience_years,
            'location': candidate.location,
            'education': [],
            'preferences': {}
        }
        
        pool_data = {
            'required_skills': pool.required_skills,
            'preferred_skills': pool.preferred_skills,
            'min_experience': pool.min_experience,
            'max_experience': pool.max_experience,
            'location': pool.locations[0] if pool.locations else '',
            'remote_ok': 'remote' in [loc.lower() for loc in pool.locations] if pool.locations else False
        }
        
        match_result = engine.calculate_comprehensive_match(candidate_data, pool_data)
        
        return JsonResponse({
            'success': True,
            'match_score': match_result['overall_score'],
            'matched_skills': match_result['matched_skills'],
            'missing_skills': match_result['missing_skills'],
            'recommendation': match_result['ai_recommendation']
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
