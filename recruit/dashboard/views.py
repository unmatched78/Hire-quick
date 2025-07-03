from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job
from applications.models import Application, Interview

@login_required
def dashboard_home(request):
    """Main dashboard view - redirects based on user type"""
    user = request.user
    
    if user.user_type == 'candidate':
        return candidate_dashboard(request)
    elif user.user_type == 'recruiter':
        return recruiter_dashboard(request)
    else:
        return admin_dashboard(request)

def candidate_dashboard(request):
    """Dashboard for candidates"""
    candidate_profile = getattr(request.user, 'candidate_profile', None)
    
    if not candidate_profile:
        messages.info(request, 'Please complete your profile to get started.')
        return redirect('accounts:profile_setup')
    
    # Get candidate's applications
    applications = Application.objects.filter(
        candidate=candidate_profile
    ).select_related('job__company').order_by('-applied_at')[:5]
    
    # Get upcoming interviews
    upcoming_interviews = Interview.objects.filter(
        application__candidate=candidate_profile,
        scheduled_at__gte=timezone.now(),
        status='scheduled'
    ).select_related('application__job').order_by('scheduled_at')[:3]
    
    # Get recommended jobs (simplified - in real app would use AI matching)
    recommended_jobs = Job.objects.filter(
        status='active'
    ).exclude(
        applications__candidate=candidate_profile
    ).select_related('company')[:5]
    
    # Application statistics
    app_stats = applications.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status__in=['applied', 'screening'])),
        interviews=Count('id', filter=Q(status='interview')),
        offers=Count('id', filter=Q(status='offer'))
    )
    
    context = {
        'candidate_profile': candidate_profile,
        'applications': applications,
        'upcoming_interviews': upcoming_interviews,
        'recommended_jobs': recommended_jobs,
        'app_stats': app_stats,
    }
    
    return render(request, 'dashboard/candidate.html', context)

def recruiter_dashboard(request):
    """Dashboard for recruiters"""
    recruiter_profile = getattr(request.user, 'recruiter_profile', None)
    
    if not recruiter_profile:
        messages.info(request, 'Please complete your profile to get started.')
        return redirect('accounts:profile_setup')
    
    # Get recruiter's jobs
    jobs = Job.objects.filter(
        recruiter=recruiter_profile
    ).select_related('company').order_by('-created_at')[:5]
    
    # Get recent applications
    recent_applications = Application.objects.filter(
        job__recruiter=recruiter_profile
    ).select_related('job', 'candidate').order_by('-applied_at')[:10]
    
    # Get upcoming interviews
    upcoming_interviews = Interview.objects.filter(
        interviewer=recruiter_profile,
        scheduled_at__gte=timezone.now(),
        status='scheduled'
    ).select_related('application__job', 'application__candidate').order_by('scheduled_at')[:5]
    
    # Statistics
    stats = {
        'active_jobs': jobs.filter(status='active').count(),
        'total_applications': recent_applications.count(),
        'pending_applications': recent_applications.filter(status__in=['applied', 'screening']).count(),
        'interviews_this_week': upcoming_interviews.filter(
            scheduled_at__lte=timezone.now() + timedelta(days=7)
        ).count(),
    }
    
    context = {
        'recruiter_profile': recruiter_profile,
        'jobs': jobs,
        'recent_applications': recent_applications,
        'upcoming_interviews': upcoming_interviews,
        'stats': stats,
    }
    
    return render(request, 'dashboard/recruiter.html', context)

def admin_dashboard(request):
    """Dashboard for admin users"""
    # Basic admin stats
    stats = {
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(status='active').count(),
        'total_applications': Application.objects.count(),
        'total_interviews': Interview.objects.count(),
    }
    
    context = {
        'stats': stats,
    }
    
    return render(request, 'dashboard/admin.html', context)
