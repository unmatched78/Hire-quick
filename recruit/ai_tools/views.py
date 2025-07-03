from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CVGenerationRequest
from .forms import CVGenerationForm, BaseProfileForm
from .ai_crew import JobApplicationCrew
import json
import os
from datetime import datetime

@login_required
def ai_tools_home(request):
    """AI Tools home page"""
    if request.user.user_type != 'candidate':
        messages.error(request, 'AI tools are only available for job seekers.')
        return redirect('dashboard:home')
    
    recent_requests = CVGenerationRequest.objects.filter(user=request.user)[:5]
    
    context = {
        'recent_requests': recent_requests,
        'ai_enabled': settings.AI_TOOLS_ENABLED,
    }
    
    return render(request, 'ai_tools/home.html', context)

@login_required
def generate_cv_cover_letter(request):
    """Generate CV and Cover Letter for a job"""
    if request.user.user_type != 'candidate':
        messages.error(request, 'AI tools are only available for job seekers.')
        return redirect('dashboard:home')
    
    if not settings.AI_TOOLS_ENABLED or not settings.OPENAI_API_KEY:
        messages.error(request, 'AI tools are currently disabled. Please contact support.')
        return redirect('ai_tools:home')
    
    if request.method == 'POST':
        form = CVGenerationForm(request.POST)
        profile_form = BaseProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            # Create the request
            cv_request = form.save(commit=False)
            cv_request.user = request.user
            cv_request.status = 'pending'
            
            # Extract job info from URL (simplified)
            job_url = form.cleaned_data['job_url']
            cv_request.job_title = "Position"  # Will be updated by AI
            cv_request.company_name = "Company"  # Will be updated by AI
            cv_request.save()
            
            # Start AI processing (in a real app, this would be async)
            try:
                crew = JobApplicationCrew()
                result = crew.process_job_application(
                    job_url=job_url,
                    user_profile=profile_form.cleaned_data,
                    request_id=cv_request.id
                )
                
                if result.get('success'):
                    cv_request.status = 'completed'
                    cv_request.completed_at = datetime.now()
                    cv_request.save()
                    messages.success(request, 'CV and Cover Letter generated successfully!')
                    return redirect('ai_tools:request_detail', pk=cv_request.pk)
                else:
                    cv_request.status = 'failed'
                    cv_request.error_message = result.get('error', 'Unknown error')
                    cv_request.save()
                    messages.error(request, f'Generation failed: {result.get("error")}')
            
            except Exception as e:
                cv_request.status = 'failed'
                cv_request.error_message = str(e)
                cv_request.save()
                messages.error(request, f'An error occurred: {str(e)}')
    
    else:
        form = CVGenerationForm()
        # Pre-populate profile form from user's profile
        initial_data = {}
        if hasattr(request.user, 'candidate_profile'):
            profile = request.user.candidate_profile
            initial_data = {
                'full_name': profile.get_full_name(),
                'current_title': profile.current_title,
                'location': profile.location,
                'email': request.user.email,
                'linkedin': profile.linkedin_url,
                'professional_summary': profile.summary,
                'skills': ', '.join(profile.skills) if profile.skills else '',
            }
        profile_form = BaseProfileForm(initial=initial_data)
    
    context = {
        'form': form,
        'profile_form': profile_form,
    }
    
    return render(request, 'ai_tools/generate.html', context)

class CVRequestListView(LoginRequiredMixin, ListView):
    model = CVGenerationRequest
    template_name = 'ai_tools/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def get_queryset(self):
        return CVGenerationRequest.objects.filter(user=self.request.user)

@login_required
def request_detail(request, pk):
    """View details of a CV generation request"""
    cv_request = get_object_or_404(CVGenerationRequest, pk=pk, user=request.user)
    
    context = {
        'request': cv_request,
    }
    
    return render(request, 'ai_tools/request_detail.html', context)

@login_required
def download_file(request, pk, file_type):
    """Download generated files"""
    cv_request = get_object_or_404(CVGenerationRequest, pk=pk, user=request.user)
    
    if cv_request.status != 'completed':
        messages.error(request, 'Files are not ready for download yet.')
        return redirect('ai_tools:request_detail', pk=pk)
    
    file_field = None
    filename = None
    
    if file_type == 'cv_pdf':
        file_field = cv_request.cv_pdf
        filename = f"CV_{cv_request.job_title}_{cv_request.company_name}.pdf"
    elif file_type == 'cv_jpg':
        file_field = cv_request.cv_jpg
        filename = f"CV_{cv_request.job_title}_{cv_request.company_name}.jpg"
    elif file_type == 'cover_letter_pdf':
        file_field = cv_request.cover_letter_pdf
        filename = f"CoverLetter_{cv_request.job_title}_{cv_request.company_name}.pdf"
    elif file_type == 'cover_letter_jpg':
        file_field = cv_request.cover_letter_jpg
        filename = f"CoverLetter_{cv_request.job_title}_{cv_request.company_name}.jpg"
    
    if file_field and file_field.name:
        response = HttpResponse(file_field.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    messages.error(request, 'File not found.')
    return redirect('ai_tools:request_detail', pk=pk)
