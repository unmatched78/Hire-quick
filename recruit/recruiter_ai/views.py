from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import json

from .models import JobGenerationRequest, InterviewSchedule, CalendarEvent
from .forms import JobGenerationForm, JobCreationFromAIForm, InterviewScheduleForm, CalendarEventForm, InterviewFeedbackForm
from .ai_agents import JobDescriptionAgent, InterviewSchedulingAgent
from applications.models import Application
from jobs.models import Job

@login_required
def ai_tools_home(request):
    """AI Tools home page for recruiters"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'AI tools are only available for recruiters.')
        return redirect('dashboard:home')
    
    recent_generations = JobGenerationRequest.objects.filter(
        recruiter=request.user.recruiter_profile
    )[:5]
    
    context = {
        'recent_generations': recent_generations,
        'ai_enabled': settings.AI_TOOLS_ENABLED and settings.OPENAI_API_KEY,
    }
    
    return render(request, 'recruiter_ai/home.html', context)

@login_required
def generate_job_description(request):
    """Generate job description using AI"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can access this feature.')
        return redirect('dashboard:home')
    
    if not (settings.AI_TOOLS_ENABLED and settings.OPENAI_API_KEY):
        messages.error(request, 'AI tools are currently disabled.')
        return redirect('recruiter_ai:home')
    
    if request.method == 'POST':
        form = JobGenerationForm(request.POST)
        if form.is_valid():
            generation_request = form.save(commit=False)
            generation_request.recruiter = request.user.recruiter_profile
            generation_request.status = 'processing'
            generation_request.save()
            
            # Generate job description using AI
            try:
                agent = JobDescriptionAgent()
                job_data = {
                    'job_title': generation_request.job_title,
                    'industry': generation_request.industry,
                    'experience_level': generation_request.experience_level,
                    'employment_type': generation_request.employment_type,
                    'remote_option': generation_request.remote_option,
                    'requirements_input': generation_request.requirements_input,
                    'company_description': generation_request.company_description,
                }
                
                result = agent.generate_job_description(job_data)
                
                if 'error' not in result:
                    generation_request.generated_description = result.get('description', '')
                    generation_request.generated_requirements = (
                        result.get('required_qualifications', []) + 
                        result.get('responsibilities', [])
                    )
                    generation_request.generated_benefits = result.get('benefits', [])
                    generation_request.generated_skills = result.get('technical_skills', [])
                    generation_request.status = 'completed'
                    generation_request.completed_at = timezone.now()
                else:
                    generation_request.status = 'failed'
                    generation_request.error_message = result.get('error', 'Unknown error')
                
                generation_request.save()
                
                if generation_request.status == 'completed':
                    messages.success(request, 'Job description generated successfully!')
                    return redirect('recruiter_ai:generation_detail', pk=generation_request.pk)
                else:
                    messages.error(request, 'Failed to generate job description. Please try again.')
            
            except Exception as e:
                generation_request.status = 'failed'
                generation_request.error_message = str(e)
                generation_request.save()
                messages.error(request, f'An error occurred: {str(e)}')
    
    else:
        form = JobGenerationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'recruiter_ai/generate_job.html', context)

@login_required
def generation_detail(request, pk):
    """View details of a job generation request"""
    generation_request = get_object_or_404(
        JobGenerationRequest, 
        pk=pk, 
        recruiter=request.user.recruiter_profile
    )
    
    context = {
        'generation_request': generation_request,
    }
    
    return render(request, 'recruiter_ai/generation_detail.html', context)

@login_required
def create_job_from_ai(request, pk):
    """Create a job posting from AI-generated content"""
    generation_request = get_object_or_404(
        JobGenerationRequest, 
        pk=pk, 
        recruiter=request.user.recruiter_profile
    )
    
    if generation_request.status != 'completed':
        messages.error(request, 'Job generation is not completed yet.')
        return redirect('recruiter_ai:generation_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobCreationFromAIForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user.recruiter_profile.company
            job.recruiter = request.user.recruiter_profile
            
            # Use AI-generated content if selected
            if form.cleaned_data.get('use_ai_description'):
                job.description = generation_request.generated_description
            
            if form.cleaned_data.get('use_ai_requirements'):
                job.requirements = generation_request.generated_requirements
            
            if form.cleaned_data.get('use_ai_benefits'):
                job.benefits = generation_request.generated_benefits
            
            # Add preferred skills
            job.preferred_skills = generation_request.generated_skills
            
            job.save()
            
            # Link the generation request to the created job
            generation_request.job_created = job
            generation_request.save()
            
            messages.success(request, 'Job posting created successfully!')
            return redirect('jobs:detail', pk=job.pk)
    
    else:
        # Pre-populate form with AI-generated content
        initial_data = {
            'title': generation_request.job_title,
            'description': generation_request.generated_description,
            'job_type': generation_request.employment_type,
            'remote_ok': generation_request.remote_option in ['remote', 'hybrid'],
        }
        form = JobCreationFromAIForm(initial=initial_data)
    
    context = {
        'form': form,
        'generation_request': generation_request,
    }
    
    return render(request, 'recruiter_ai/create_job_from_ai.html', context)

# Calendar and Interview Scheduling Views

@login_required
def calendar_view(request):
    """Calendar view for recruiters"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can access the calendar.')
        return redirect('dashboard:home')
    
    # Get current month's events
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    interviews = InterviewSchedule.objects.filter(
        interviewer=request.user.recruiter_profile,
        scheduled_date__range=[start_of_month, end_of_month]
    ).select_related('application__candidate', 'application__job')
    
    events = CalendarEvent.objects.filter(
        recruiter=request.user.recruiter_profile,
        start_date__range=[start_of_month, end_of_month]
    )
    
    # Upcoming interviews (next 7 days)
    upcoming_interviews = InterviewSchedule.objects.filter(
        interviewer=request.user.recruiter_profile,
        scheduled_date__range=[today, today + timedelta(days=7)],
        status__in=['scheduled', 'confirmed']
    ).select_related('application__candidate', 'application__job')
    
    context = {
        'interviews': interviews,
        'events': events,
        'upcoming_interviews': upcoming_interviews,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'recruiter_ai/calendar.html', context)

@login_required
def schedule_interview(request, application_id):
    """Schedule an interview for an application"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can schedule interviews.')
        return redirect('dashboard:home')
    
    application = get_object_or_404(
        Application,
        pk=application_id,
        job__recruiter=request.user.recruiter_profile
    )
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.interviewer = request.user.recruiter_profile
            interview.save()
            
            # Create calendar event
            CalendarEvent.objects.create(
                recruiter=request.user.recruiter_profile,
                title=f"Interview: {application.candidate.get_full_name()}",
                description=f"Interview for {application.job.title} position",
                event_type='interview',
                start_date=interview.scheduled_date,
                start_time=interview.scheduled_time,
                end_date=interview.scheduled_date,
                end_time=(datetime.combine(interview.scheduled_date, interview.scheduled_time) + 
                         timedelta(minutes=interview.duration_minutes)).time(),
                interview_schedule=interview,
                application=application
            )
            
            # Send email notification
            send_interview_notification(interview)
            
            # Update application status
            application.status = 'interview'
            application.save()
            
            messages.success(request, 'Interview scheduled successfully!')
            return redirect('applications:detail', pk=application.pk)
    
    else:
        form = InterviewScheduleForm()
        
        # AI suggestion for interview structure
        if settings.AI_TOOLS_ENABLED and settings.OPENAI_API_KEY:
            try:
                agent = InterviewSchedulingAgent()
                suggestions = agent.suggest_interview_structure(
                    application.job.title,
                    'mid',  # Default experience level
                    'video'  # Default interview type
                )
                messages.info(request, f"AI Suggestion: {suggestions[:200]}...")
            except:
                pass
    
    context = {
        'form': form,
        'application': application,
    }
    
    return render(request, 'recruiter_ai/schedule_interview.html', context)

@login_required
def interview_detail(request, pk):
    """View interview details"""
    interview = get_object_or_404(
        InterviewSchedule,
        pk=pk,
        interviewer=request.user.recruiter_profile
    )
    
    context = {
        'interview': interview,
    }
    
    return render(request, 'recruiter_ai/interview_detail.html', context)

@login_required
def interview_feedback(request, pk):
    """Add feedback to an interview"""
    interview = get_object_or_404(
        InterviewSchedule,
        pk=pk,
        interviewer=request.user.recruiter_profile
    )
    
    if request.method == 'POST':
        form = InterviewFeedbackForm(request.POST, instance=interview)
        if form.is_valid():
            interview = form.save()
            
            # Update application status based on recommendation
            if interview.recommendation == 'hire':
                interview.application.status = 'offer'
            elif interview.recommendation == 'no_hire':
                interview.application.status = 'rejected'
            
            interview.application.save()
            
            messages.success(request, 'Interview feedback saved successfully!')
            return redirect('recruiter_ai:interview_detail', pk=interview.pk)
    
    else:
        form = InterviewFeedbackForm(instance=interview)
    
    context = {
        'form': form,
        'interview': interview,
    }
    
    return render(request, 'recruiter_ai/interview_feedback.html', context)

def send_interview_notification(interview):
    """Send email notification for scheduled interview"""
    try:
        agent = InterviewSchedulingAgent()
        template = agent.generate_email_templates('interview_invitation')
        
        subject = f"Interview Invitation - {interview.application.job.title} Position"
        
        # Format email content
        email_content = template.format(
            candidate_name=interview.application.candidate.get_full_name(),
            job_title=interview.application.job.title,
            company_name=interview.application.job.company.name,
            interview_date=interview.scheduled_date.strftime('%B %d, %Y'),
            interview_time=interview.scheduled_time.strftime('%I:%M %p'),
            duration=interview.duration_minutes,
            interview_type=interview.get_interview_type_display(),
            location_or_link=interview.meeting_link or interview.location,
            interviewer_name=interview.interviewer.get_full_name(),
        )
        
        send_mail(
            subject=subject,
            message=email_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[interview.application.candidate.user.email],
            fail_silently=False,
        )
        
        interview.candidate_notified = True
        interview.save()
        
    except Exception as e:
        print(f"Failed to send interview notification: {e}")

@login_required
def get_interview_suggestions(request):
    """AJAX endpoint for AI interview suggestions"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'error': 'Permission denied'})
    
    job_title = request.GET.get('job_title', '')
    skills = request.GET.get('skills', '').split(',')
    experience_level = request.GET.get('experience_level', 'mid')
    
    if settings.AI_TOOLS_ENABLED and settings.OPENAI_API_KEY:
        try:
            agent = JobDescriptionAgent()
            questions = agent.generate_interview_questions(job_title, skills, experience_level)
            return JsonResponse({'success': True, 'questions': questions})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'AI tools not available'})
