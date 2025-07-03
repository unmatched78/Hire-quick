from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.conf import settings
import os
import json
from .models import Application, ParsedResume, ApplicationFile
from jobs.models import Job
import sys
sys.path.append(os.path.join(settings.BASE_DIR, 'scripts'))
from resume_parser import ResumeParser

@login_required
@require_POST
def parse_resume(request, application_id):
    """Parse resume for an application"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Only recruiters can parse resumes'})
    
    application = get_object_or_404(
        Application, 
        pk=application_id,
        job__recruiter=request.user.recruiter_profile
    )
    
    try:
        # Find resume file
        resume_file = None
        
        # Check traditional resume field
        if application.resume:
            resume_file = application.resume
        else:
            # Check uploaded files for resume
            resume_files = application.uploaded_files.filter(
                form_field__field_type__in=['resume', 'file'],
                is_document=True
            ).first()
            
            if resume_files:
                resume_file = resume_files.file
        
        if not resume_file:
            return JsonResponse({'success': False, 'error': 'No resume file found'})
        
        # Initialize parser
        parser = ResumeParser()
        
        # Parse the resume
        file_path = resume_file.path
        parsed_data = parser.parse_resume(file_path)
        
        if 'error' in parsed_data:
            return JsonResponse({'success': False, 'error': parsed_data['error']})
        
        # Calculate skill match with job requirements
        job_requirements = application.job.requirements or []
        skill_match = parser.calculate_skill_match(parsed_data.get('skills', {}), job_requirements)
        
        # Create or update ParsedResume
        parsed_resume, created = ParsedResume.objects.get_or_create(
            application=application,
            defaults={
                'full_name': parsed_data.get('contact_info', {}).get('name', ''),
                'email': parsed_data.get('contact_info', {}).get('email', ''),
                'phone': parsed_data.get('contact_info', {}).get('phone', ''),
                'linkedin_url': parsed_data.get('contact_info', {}).get('linkedin', ''),
                'github_url': parsed_data.get('contact_info', {}).get('github', ''),
                'website_url': parsed_data.get('contact_info', {}).get('website', ''),
                'skills_data': parsed_data.get('skills', {}),
                'total_experience_years': parsed_data.get('total_experience_years', 0),
                'experience_data': parsed_data.get('experience', []),
                'education_data': parsed_data.get('education', []),
                'certifications_data': parsed_data.get('certifications', []),
                'languages_data': parsed_data.get('languages', []),
                'raw_text': parsed_data.get('raw_text', ''),
                'skill_match_percentage': skill_match.get('match_percentage', 0),
                'matched_skills': skill_match.get('matched_skills', []),
                'missing_skills': skill_match.get('missing_skills', []),
            }
        )
        
        # Update AI analysis if available
        ai_analysis = parsed_data.get('ai_analysis', {})
        if ai_analysis and 'error' not in ai_analysis:
            parsed_resume.ai_score = ai_analysis.get('score', 0)
            parsed_resume.ai_strengths = ai_analysis.get('strengths', [])
            parsed_resume.ai_improvements = ai_analysis.get('improvements', [])
            parsed_resume.ai_suitable_roles = ai_analysis.get('suitable_roles', [])
            parsed_resume.career_level = ai_analysis.get('career_level', '')
        
        parsed_resume.save()
        
        # Mark file as processed
        if hasattr(resume_file, 'applicationfile'):
            resume_file.applicationfile.parsing_status = 'completed'
            resume_file.applicationfile.is_resume = True
            resume_file.applicationfile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Resume parsed successfully',
            'data': {
                'skill_match_percentage': parsed_resume.skill_match_percentage,
                'total_experience_years': parsed_resume.total_experience_years,
                'ai_score': parsed_resume.ai_score,
                'career_level': parsed_resume.career_level
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Parsing failed: {str(e)}'})

@login_required
def view_parsed_resume(request, application_id):
    """View parsed resume details"""
    application = get_object_or_404(Application, pk=application_id)
    
    # Check permissions
    if request.user.user_type == 'candidate':
        if application.candidate.user != request.user:
            messages.error(request, 'You can only view your own applications.')
            return redirect('applications:my_applications')
    elif request.user.user_type == 'recruiter':
        if application.job.recruiter.user != request.user:
            messages.error(request, 'You can only view applications for your jobs.')
            return redirect('applications:recruiter_applications')
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:home')
    
    try:
        parsed_resume = application.parsed_resume
    except ParsedResume.DoesNotExist:
        messages.error(request, 'Resume has not been parsed yet.')
        return redirect('applications:detail', pk=application_id)
    
    return render(request, 'applications/parsed_resume_detail.html', {
        'application': application,
        'parsed_resume': parsed_resume,
        'job': application.job
    })

class ParsedResumeListView(LoginRequiredMixin, ListView):
    """List all parsed resumes for a recruiter"""
    model = ParsedResume
    template_name = 'applications/parsed_resume_list.html'
    context_object_name = 'parsed_resumes'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can view this page.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = ParsedResume.objects.filter(
            application__job__recruiter=self.request.user.recruiter_profile
        ).select_related('application__candidate', 'application__job')
        
        # Filter by job
        job_id = self.request.GET.get('job')
        if job_id:
            queryset = queryset.filter(application__job_id=job_id)
        
        # Filter by skill match percentage
        min_match = self.request.GET.get('min_match')
        if min_match:
            try:
                min_match = float(min_match)
                queryset = queryset.filter(skill_match_percentage__gte=min_match)
            except ValueError:
                pass
        
        # Filter by experience years
        min_experience = self.request.GET.get('min_experience')
        if min_experience:
            try:
                min_experience = float(min_experience)
                queryset = queryset.filter(total_experience_years__gte=min_experience)
            except ValueError:
                pass
        
        # Filter by career level
        career_level = self.request.GET.get('career_level')
        if career_level:
            queryset = queryset.filter(career_level__icontains=career_level)
        
        # Sort by skill match percentage by default
        sort_by = self.request.GET.get('sort', '-skill_match_percentage')
        if sort_by in ['-skill_match_percentage', 'skill_match_percentage', 
                       '-total_experience_years', 'total_experience_years',
                       '-ai_score', 'ai_score', '-parsed_at', 'parsed_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recruiter_jobs'] = Job.objects.filter(
            recruiter=self.request.user.recruiter_profile
        ).order_by('-created_at')
        
        # Statistics
        all_parsed = ParsedResume.objects.filter(
            application__job__recruiter=self.request.user.recruiter_profile
        )
        
        context['stats'] = {
            'total_parsed': all_parsed.count(),
            'high_match': all_parsed.filter(skill_match_percentage__gte=80).count(),
            'medium_match': all_parsed.filter(
                skill_match_percentage__gte=60, 
                skill_match_percentage__lt=80
            ).count(),
            'low_match': all_parsed.filter(skill_match_percentage__lt=60).count(),
            'avg_experience': all_parsed.aggregate(
                avg_exp=models.Avg('total_experience_years')
            )['avg_exp'] or 0,
        }
        
        return context

@login_required
@require_POST
def bulk_parse_resumes(request):
    """Parse multiple resumes in bulk"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    application_ids = request.POST.getlist('applications')
    
    applications = Application.objects.filter(
        id__in=application_ids,
        job__recruiter=request.user.recruiter_profile
    )
    
    parser = ResumeParser()
    parsed_count = 0
    errors = []
    
    for application in applications:
        try:
            # Skip if already parsed
            if hasattr(application, 'parsed_resume'):
                continue
            
            # Find resume file
            resume_file = None
            if application.resume:
                resume_file = application.resume
            else:
                resume_files = application.uploaded_files.filter(
                    form_field__field_type__in=['resume', 'file'],
                    is_document=True
                ).first()
                if resume_files:
                    resume_file = resume_files.file
            
            if not resume_file:
                errors.append(f"No resume found for {application.candidate.get_full_name()}")
                continue
            
            # Parse resume
            parsed_data = parser.parse_resume(resume_file.path)
            
            if 'error' in parsed_data:
                errors.append(f"Parsing failed for {application.candidate.get_full_name()}: {parsed_data['error']}")
                continue
            
            # Calculate skill match
            job_requirements = application.job.requirements or []
            skill_match = parser.calculate_skill_match(parsed_data.get('skills', {}), job_requirements)
            
            # Create ParsedResume
            ParsedResume.objects.create(
                application=application,
                full_name=parsed_data.get('contact_info', {}).get('name', ''),
                email=parsed_data.get('contact_info', {}).get('email', ''),
                phone=parsed_data.get('contact_info', {}).get('phone', ''),
                linkedin_url=parsed_data.get('contact_info', {}).get('linkedin', ''),
                github_url=parsed_data.get('contact_info', {}).get('github', ''),
                website_url=parsed_data.get('contact_info', {}).get('website', ''),
                skills_data=parsed_data.get('skills', {}),
                total_experience_years=parsed_data.get('total_experience_years', 0),
                experience_data=parsed_data.get('experience', []),
                education_data=parsed_data.get('education', []),
                certifications_data=parsed_data.get('certifications', []),
                languages_data=parsed_data.get('languages', []),
                raw_text=parsed_data.get('raw_text', ''),
                skill_match_percentage=skill_match.get('match_percentage', 0),
                matched_skills=skill_match.get('matched_skills', []),
                missing_skills=skill_match.get('missing_skills', []),
            )
            
            parsed_count += 1
            
        except Exception as e:
            errors.append(f"Error parsing {application.candidate.get_full_name()}: {str(e)}")
    
    return JsonResponse({
        'success': True,
        'parsed_count': parsed_count,
        'errors': errors,
        'message': f'Successfully parsed {parsed_count} resumes'
    })

@login_required
def resume_analytics(request):
    """Show resume analytics dashboard"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view analytics.')
        return redirect('dashboard:home')
    
    parsed_resumes = ParsedResume.objects.filter(
        application__job__recruiter=request.user.recruiter_profile
    )
    
    # Skill analysis
    all_skills = {}
    for resume in parsed_resumes:
        for category, skills in resume.skills_data.items():
            if category not in all_skills:
                all_skills[category] = {}
            for skill in skills:
                all_skills[category][skill] = all_skills[category].get(skill, 0) + 1
    
    # Top skills by category
    top_skills = {}
    for category, skills in all_skills.items():
        top_skills[category] = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Experience distribution
    experience_ranges = {
        '0-2 years': parsed_resumes.filter(total_experience_years__lt=2).count(),
        '2-5 years': parsed_resumes.filter(total_experience_years__gte=2, total_experience_years__lt=5).count(),
        '5-10 years': parsed_resumes.filter(total_experience_years__gte=5, total_experience_years__lt=10).count(),
        '10+ years': parsed_resumes.filter(total_experience_years__gte=10).count(),
    }
    
    # Match score distribution
    match_ranges = {
        '80-100%': parsed_resumes.filter(skill_match_percentage__gte=80).count(),
        '60-79%': parsed_resumes.filter(skill_match_percentage__gte=60, skill_match_percentage__lt=80).count(),
        '40-59%': parsed_resumes.filter(skill_match_percentage__gte=40, skill_match_percentage__lt=60).count(),
        '0-39%': parsed_resumes.filter(skill_match_percentage__lt=40).count(),
    }
    
    context = {
        'total_parsed': parsed_resumes.count(),
        'top_skills': top_skills,
        'experience_ranges': experience_ranges,
        'match_ranges': match_ranges,
        'avg_match_score': parsed_resumes.aggregate(
            avg_match=models.Avg('skill_match_percentage')
        )['avg_match'] or 0,
        'avg_experience': parsed_resumes.aggregate(
            avg_exp=models.Avg('total_experience_years')
        )['avg_exp'] or 0,
    }
    
    return render(request, 'applications/resume_analytics.html', context)
