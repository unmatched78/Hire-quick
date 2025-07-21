from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
import os
import json
import mimetypes
from .models import Application, ParsedResume, ApplicationFile, Interview
from .forms import ApplicationForm, ApplicationStatusForm, InterviewForm, ApplicationNotesForm
from jobs.models import Job, ApplicationFormField, ApplicationForm as JobApplicationForm
from accounts.models import CandidateProfile, RecruiterProfile
import sys
sys.path.append(os.path.join(settings.BASE_DIR, 'scripts'))
from resume_parser import ResumeParser

# Include the resume parsing views
from .resume_parsing_views import (
    parse_resume, view_parsed_resume, ParsedResumeListView, 
    bulk_parse_resumes, resume_analytics
)

@login_required
def apply_for_job(request, job_id):
    """Apply for a job with dynamic form"""
    job = get_object_or_404(Job, pk=job_id, is_active=True)
    
    # Check if user already applied
    if request.user.user_type == 'candidate':
        if Application.objects.filter(job=job, candidate=request.user.candidate_profile).exists():
            messages.warning(request, 'You have already applied for this job.')
            return redirect('jobs:detail', pk=job_id)
    else:
        messages.error(request, 'Only candidates can apply for jobs.')
        return redirect('jobs:detail', pk=job_id)
    
    # Get the job's application form
    try:
        application_form = job.application_form
        form_fields = application_form.fields.all().order_by('order')
    except JobApplicationForm.DoesNotExist:
        # If no custom form, use default fields
        application_form = None
        form_fields = []
    
    if request.method == 'POST':
        # Process form submission
        try:
            # Create application
            application = Application.objects.create(
                job=job,
                candidate=request.user.candidate_profile,
                status='applied',
                form_responses={}
            )
            
            # Process each form field
            for field in form_fields:
                field_id = str(field.id)
                
                if field.field_type in ['file', 'resume', 'video', 'audio', 'image']:
                    # Handle file uploads
                    if field_id in request.FILES:
                        uploaded_file = request.FILES[field_id]
                        
                        # Create ApplicationFile
                        file_obj = ApplicationFile.objects.create(
                            application=application,
                            form_field=field,
                            file=uploaded_file,
                            original_filename=uploaded_file.name,
                            file_size=uploaded_file.size,
                            content_type=uploaded_file.content_type or mimetypes.guess_type(uploaded_file.name)[0],
                            is_resume=field.field_type == 'resume'
                        )
                        
                        # Store reference in form_responses
                        application.form_responses[field_id] = {
                            'file_path': file_obj.file.url,
                            'original_name': uploaded_file.name,
                            'file_type': file_obj.content_type
                        }
                else:
                    # Handle text fields
                    if field_id in request.POST:
                        application.form_responses[field_id] = request.POST[field_id]
            
            # Save the application with form responses
            application.save()
            
            # If there's a resume, trigger parsing
            resume_files = application.uploaded_files.filter(is_resume=True)
            if resume_files.exists():
                # Mark for background processing
                resume_files.update(parsing_status='pending')
            
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('applications:my_applications')
            
        except Exception as e:
            messages.error(request, f'Error submitting application: {str(e)}')
    
    return render(request, 'applications/apply_dynamic.html', {
        'job': job,
        'application_form': application_form,
        'form_fields': form_fields
    })

class MyApplicationsView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/my_applications.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'candidate':
            messages.error(request, 'Only candidates can view applications.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Application.objects.filter(
            candidate=self.request.user.candidate_profile
        ).select_related('job__company').order_by('-applied_at')

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'applications/detail.html'
    context_object_name = 'application'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interviews'] = self.object.interviews.all().order_by('scheduled_at')
        context['uploaded_files'] = self.object.uploaded_files.all().order_by('-uploaded_at')
        
        # Get form fields for display
        if self.object.job.application_form:
            context['form_fields'] = self.object.job.application_form.fields.all().order_by('order')
        
        # Check if user can manage this application
        user = self.request.user
        context['can_manage'] = (
            user.user_type == 'recruiter' and 
            self.object.job.recruiter == user.recruiter_profile
        )
        
        return context

class RecruiterApplicationsView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/recruiter_applications.html'
    context_object_name = 'applications'
    paginate_by = 15
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can view this page.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Application.objects.filter(
            job__recruiter=self.request.user.recruiter_profile
        ).select_related('job', 'candidate').annotate(
            interview_count=Count('interviews')
        )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by job
        job_id = self.request.GET.get('job')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        # Search by candidate name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(candidate__first_name__icontains=search) |
                Q(candidate__last_name__icontains=search) |
                Q(candidate__user__email__icontains=search)
            )
        
        return queryset.order_by('-applied_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Application.STATUS_CHOICES
        context['recruiter_jobs'] = Job.objects.filter(
            recruiter=self.request.user.recruiter_profile
        ).order_by('-created_at')
        
        # Application statistics
        all_applications = Application.objects.filter(
            job__recruiter=self.request.user.recruiter_profile
        )
        context['stats'] = {
            'total': all_applications.count(),
            'pending': all_applications.filter(status__in=['applied', 'screening']).count(),
            'interviews': all_applications.filter(status='interview').count(),
            'offers': all_applications.filter(status='offer').count(),
            'hired': all_applications.filter(status='hired').count(),
        }
        
        return context

@login_required
@require_POST
def quick_update_status(request, pk):
    """Quick AJAX status update"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    application = get_object_or_404(
        Application, 
        pk=pk, 
        job__recruiter=request.user.recruiter_profile
    )
    
    new_status = request.POST.get('status')
    if new_status in dict(Application.STATUS_CHOICES):
        application.status = new_status
        application.save()
        
        return JsonResponse({
            'success': True,
            'status': application.get_status_display(),
            'badge_class': application.get_status_badge_class()
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid status'})

@login_required
def update_application_status(request, pk):
    """Update application status (recruiter only)"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can update application status.')
        return redirect('dashboard:home')
    
    application = get_object_or_404(
        Application, 
        pk=pk,
        job__recruiter=request.user.recruiter_profile
    )
    
    form = ApplicationStatusForm(request.POST, instance=application)
    if form.is_valid():
        application = form.save()
        
        # Add notes if provided
        notes = request.POST.get('notes')
        if notes:
            if application.notes:
                application.notes += f"\n\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
            else:
                application.notes = f"[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
            application.save()
        
        messages.success(request, f'Application status updated to {application.get_status_display()}')
        return HttpResponseRedirect(reverse('applications:detail', args=[pk]))
    
    messages.error(request, 'Error updating application status')
    return HttpResponseRedirect(reverse('applications:detail', args=[pk]))

@login_required
@require_POST
def add_application_notes(request, pk):
    """Add notes to an application"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    application = get_object_or_404(
        Application, 
        pk=pk,
        job__recruiter=request.user.recruiter_profile
    )
    
    form = ApplicationNotesForm(request.POST, instance=application)
    if form.is_valid():
        application = form.save()
        messages.success(request, 'Notes updated successfully')
        return HttpResponseRedirect(reverse('applications:detail', args=[pk]))
    
    messages.error(request, 'Error updating notes')
    return HttpResponseRedirect(reverse('applications:detail', args=[pk]))

@login_required
@require_POST
def schedule_interview(request, pk):
    """Schedule an interview for an application"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    application = get_object_or_404(
        Application, 
        pk=pk,
        job__recruiter=request.user.recruiter_profile
    )
    
    form = InterviewForm(request.POST)
    if form.is_valid():
        interview = form.save(commit=False)
        interview.application = application
        interview.interviewer = request.user.recruiter_profile
        interview.save()
        
        # Update application status if needed
        if application.status not in ['interview', 'offer', 'hired']:
            application.status = 'interview'
            application.save()
        
        messages.success(request, 'Interview scheduled successfully')
        return HttpResponseRedirect(reverse('applications:detail', args=[pk]))
    
    messages.error(request, 'Error scheduling interview')
    return HttpResponseRedirect(reverse('applications:detail', args=[pk]))

@login_required
def interview_detail(request, pk):
    """View interview details"""
    interview = get_object_or_404(Interview, pk=pk)
    
    # Check permissions
    if request.user.user_type == 'candidate':
        if interview.application.candidate.user != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('applications:my_applications')
    elif request.user.user_type == 'recruiter':
        if interview.interviewer.user != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('applications:recruiter_applications')
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:home')
    
    return render(request, 'applications/interview_detail.html', {
        'interview': interview
    })

@login_required
def download_file(request, file_id):
    """Download an uploaded file"""
    file_obj = get_object_or_404(ApplicationFile, pk=file_id)
    
    # Check permissions
    if request.user.user_type == 'candidate':
        if file_obj.application.candidate.user != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('applications:my_applications')
    elif request.user.user_type == 'recruiter':
        if file_obj.application.job.recruiter.user != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('applications:recruiter_applications')
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:home')
    
    # Serve the file
    from django.http import FileResponse
    response = FileResponse(
        file_obj.file.open('rb'),
        as_attachment=True,
        filename=file_obj.original_filename
    )
    return response

class ApplicationListView(LoginRequiredMixin, ListView):
    """Generic application list view"""
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.user_type == 'candidate':
            return Application.objects.filter(
                candidate=self.request.user.candidate_profile
            ).select_related('job', 'job__company').order_by('-applied_at')
        elif self.request.user.user_type == 'recruiter':
            return Application.objects.filter(
                job__recruiter=self.request.user.recruiter_profile
            ).select_related('job', 'candidate', 'candidate__user').order_by('-applied_at')
        else:
            return Application.objects.none()

# Resume parsing views are imported from resume_parsing_views.py
