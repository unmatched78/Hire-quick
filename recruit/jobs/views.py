from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Job, SavedJob, ApplicationFormField
from .forms import JobForm, JobSearchForm, ApplicationFormFieldForm, DynamicApplicationForm

class JobListView(ListView):
    model = Job
    template_name = 'jobs/list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Job.objects.filter(status='active').select_related('company', 'recruiter')
        
        # Search functionality
        search = self.request.GET.get('search')
        location = self.request.GET.get('location')
        job_type = self.request.GET.get('job_type')
        remote_ok = self.request.GET.get('remote_ok')
        salary_min = self.request.GET.get('salary_min')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company__name__icontains=search) |
                Q(description__icontains=search)
            )
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        if remote_ok:
            queryset = queryset.filter(remote_ok=True)
        
        if salary_min:
            try:
                salary_min = int(salary_min)
                queryset = queryset.filter(salary_min__gte=salary_min)
            except ValueError:
                pass
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        context['total_jobs'] = self.get_queryset().count()
        return context

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/detail.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and self.request.user.user_type == 'candidate':
            candidate_profile = getattr(self.request.user, 'candidate_profile', None)
            if candidate_profile:
                context['is_saved'] = SavedJob.objects.filter(
                    candidate=candidate_profile, 
                    job=self.object
                ).exists()
                context['has_applied'] = self.object.applications.filter(
                    candidate=candidate_profile
                ).exists()
        
        # Get custom application form fields
        context['custom_form_fields'] = self.object.application_form_fields.all().order_by('order')
        
        # Related jobs from same company
        context['related_jobs'] = Job.objects.filter(
            company=self.object.company,
            status='active'
        ).exclude(pk=self.object.pk)[:3]
        
        return context

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can post jobs.')
            return redirect('jobs:list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.recruiter = self.request.user.recruiter_profile
        form.instance.company = self.request.user.recruiter_profile.company
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        if self.object.has_custom_application_form:
            return reverse_lazy('jobs:setup_application_form', kwargs={'pk': self.object.pk})
        return self.object.get_absolute_url()

class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/update.html'
    
    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        if request.user.user_type != 'recruiter' or job.recruiter.user != request.user:
            messages.error(request, 'You can only edit your own job postings.')
            return redirect('jobs:detail', pk=job.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Job updated successfully!')
        return super().form_valid(form)

@login_required
def setup_application_form(request, pk):
    """Setup custom application form for a job"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can setup application forms.')
        return redirect('jobs:list')
    
    job = get_object_or_404(Job, pk=pk, recruiter=request.user.recruiter_profile)
    
    if not job.has_custom_application_form:
        messages.error(request, 'This job does not have custom application form enabled.')
        return redirect('jobs:detail', pk=pk)
    
    existing_fields = job.application_form_fields.all().order_by('order')
    
    return render(request, 'jobs/setup_application_form.html', {
        'job': job,
        'existing_fields': existing_fields,
    })

@login_required
@require_POST
def add_application_form_field(request, pk):
    """Add a new field to application form via AJAX"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    job = get_object_or_404(Job, pk=pk, recruiter=request.user.recruiter_profile)
    
    form = ApplicationFormFieldForm(request.POST)
    if form.is_valid():
        field = form.save(commit=False)
        field.job = job
        
        # Set order
        max_order = job.application_form_fields.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        field.order = max_order + 1
        
        field.save()
        
        return JsonResponse({
            'success': True,
            'field_id': field.id,
            'field_html': render_field_preview(field)
        })
    
    return JsonResponse({
        'success': False,
        'errors': form.errors
    })

@login_required
@require_POST
def delete_application_form_field(request, pk, field_id):
    """Delete an application form field"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    job = get_object_or_404(Job, pk=pk, recruiter=request.user.recruiter_profile)
    field = get_object_or_404(ApplicationFormField, id=field_id, job=job)
    
    field.delete()
    
    return JsonResponse({'success': True})

@login_required
@require_POST
def reorder_application_form_fields(request, pk):
    """Reorder application form fields"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    job = get_object_or_404(Job, pk=pk, recruiter=request.user.recruiter_profile)
    
    field_ids = request.POST.getlist('field_ids[]')
    
    for index, field_id in enumerate(field_ids):
        ApplicationFormField.objects.filter(
            id=field_id, 
            job=job
        ).update(order=index + 1)
    
    return JsonResponse({'success': True})

def render_field_preview(field):
    """Render HTML preview of a form field"""
    field_type_icons = {
        'text': 'fas fa-font',
        'textarea': 'fas fa-align-left',
        'email': 'fas fa-envelope',
        'phone': 'fas fa-phone',
        'number': 'fas fa-hashtag',
        'date': 'fas fa-calendar',
        'file': 'fas fa-file',
        'resume': 'fas fa-file-alt',
        'cover_letter': 'fas fa-file-text',
        'video': 'fas fa-video',
        'audio': 'fas fa-microphone',
        'url': 'fas fa-link',
        'select': 'fas fa-list',
        'radio': 'fas fa-dot-circle',
        'checkbox': 'fas fa-check-square',
        'boolean': 'fas fa-toggle-on',
        'rating': 'fas fa-star',
        'linkedin': 'fab fa-linkedin',
        'github': 'fab fa-github',
        'portfolio': 'fas fa-briefcase',
    }
    
    icon = field_type_icons.get(field.field_type, 'fas fa-question')
    required_badge = '<span class="badge badge-danger ms-2">Required</span>' if field.is_required else ''
    
    return f'''
    <div class="field-preview" data-field-id="{field.id}">
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <i class="{icon} me-2"></i>
                <strong>{field.label}</strong>
                {required_badge}
                <div class="text-muted small">{field.get_field_type_display()}</div>
                {f'<div class="text-muted small">{field.help_text}</div>' if field.help_text else ''}
            </div>
            <div class="btn-group">
                <button class="btn btn-sm btn-outline-primary edit-field-btn" data-field-id="{field.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-field-btn" data-field-id="{field.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    </div>
    '''

@login_required
def save_job(request, pk):
    """Save/unsave a job for a candidate"""
    if request.user.user_type != 'candidate':
        messages.error(request, 'Only candidates can save jobs.')
        return redirect('jobs:detail', pk=pk)
    
    job = get_object_or_404(Job, pk=pk)
    candidate_profile = request.user.candidate_profile
    
    saved_job, created = SavedJob.objects.get_or_create(
        candidate=candidate_profile,
        job=job
    )
    
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        saved_job.delete()
        messages.success(request, 'Job removed from saved jobs.')
    
    return redirect('jobs:detail', pk=pk)

@login_required
def saved_jobs(request):
    """View saved jobs for a candidate"""
    if request.user.user_type != 'candidate':
        messages.error(request, 'Only candidates can view saved jobs.')
        return redirect('jobs:list')
    
    candidate_profile = request.user.candidate_profile
    saved_jobs = SavedJob.objects.filter(candidate=candidate_profile).select_related('job__company')
    
    return render(request, 'jobs/saved_jobs.html', {'saved_jobs': saved_jobs})
