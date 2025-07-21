from django.shortcuts import render
from jobs.models import Job

def home_view(request):
    """Home page view with latest jobs"""
    latest_jobs = Job.objects.filter(status='active').select_related('company').order_by('-created_at')[:10]
    
    context = {
        'latest_jobs': latest_jobs,
    }
    
    return render(request, 'home.html', context)
