from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q, Count, Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import uuid
from datetime import timedelta
import hashlib

from .models import (
    BackgroundCheckRequest, BackgroundCheckPackage, VerificationDocument,
    IndividualCheck, VerificationAlert, ComplianceLog, VerificationTemplate
)
from .forms import (
    BackgroundCheckRequestForm, DocumentUploadForm, ConsentForm,
    PackageSelectionForm, DocumentReviewForm, CheckStatusUpdateForm,
    EmailTemplateForm, BulkActionForm
)
from .ai_verification import DocumentVerificationAI, BackgroundCheckAI
from applications.models import Application

@login_required
def verification_dashboard(request):
    """Main dashboard for background verification"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can access background verification.')
        return redirect('dashboard:home')
    
    recruiter = request.user.recruiter_profile
    
    # Get statistics
    total_requests = BackgroundCheckRequest.objects.filter(recruiter=recruiter).count()
    pending_requests = BackgroundCheckRequest.objects.filter(
        recruiter=recruiter, 
        status__in=['draft', 'pending_consent', 'consent_given', 'in_progress']
    ).count()
    completed_requests = BackgroundCheckRequest.objects.filter(
        recruiter=recruiter, 
        status='completed'
    ).count()
    
    # Recent requests
    recent_requests = BackgroundCheckRequest.objects.filter(
        recruiter=recruiter
    ).select_related('application__candidate', 'package')[:10]
    
    # Alerts requiring attention
    alerts = VerificationAlert.objects.filter(
        individual_check__background_check__recruiter=recruiter,
        reviewed=False,
        severity__in=['high', 'critical']
    )[:5]
    
    # Pending documents
    pending_documents = VerificationDocument.objects.filter(
        background_check__recruiter=recruiter,
        status='pending'
    )[:5]
    
    context = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'recent_requests': recent_requests,
        'alerts': alerts,
        'pending_documents': pending_documents,
    }
    
    return render(request, 'background_verification/dashboard.html', context)

@login_required
def create_background_check(request, application_id):
    """Create a new background check request"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can create background checks.')
        return redirect('dashboard:home')
    
    application = get_object_or_404(
        Application,
        pk=application_id,
        job__recruiter=request.user.recruiter_profile
    )
    
    # Check if background check already exists
    existing_check = BackgroundCheckRequest.objects.filter(application=application).first()
    if existing_check:
        messages.warning(request, 'Background check already exists for this candidate.')
        return redirect('background_verification:request_detail', request_id=existing_check.request_id)
    
    if request.method == 'POST':
        form = BackgroundCheckRequestForm(request.POST)
        if form.is_valid():
            background_check = form.save(commit=False)
            background_check.application = application
            background_check.recruiter = request.user.recruiter_profile
            background_check.candidate_email = application.candidate.user.email
            
            # Calculate estimated cost and due date
            package = background_check.package
            background_check.estimated_cost = package.estimated_cost
            if background_check.rush_processing:
                background_check.estimated_cost *= 1.5
                background_check.due_date = timezone.now() + timedelta(days=1)
            else:
                background_check.due_date = timezone.now() + timedelta(days=package.estimated_turnaround_days)
            
            background_check.save()
            
            # Create individual checks based on package
            create_individual_checks(background_check)
            
            # Log compliance action
            ComplianceLog.objects.create(
                background_check=background_check,
                action_type='request_created',
                description=f'Background check request created for {application.candidate.get_full_name()}',
                performed_by=request.user
            )
            
            # Send consent request email
            send_consent_request_email(background_check)
            
            messages.success(request, 'Background check request created successfully!')
            return redirect('background_verification:request_detail', request_id=background_check.request_id)
    
    else:
        # Pre-populate form with candidate information
        initial_data = {
            'candidate_first_name': application.candidate.first_name,
            'candidate_last_name': application.candidate.last_name,
            'candidate_email': application.candidate.user.email,
            'candidate_phone': application.candidate.user.phone,
            'candidate_address': application.candidate.location,
        }
        form = BackgroundCheckRequestForm(initial=initial_data)
    
    context = {
        'form': form,
        'application': application,
        'packages': BackgroundCheckPackage.objects.filter(is_active=True),
    }
    
    return render(request, 'background_verification/create_request.html', context)

def create_individual_checks(background_check):
    """Create individual checks based on package configuration"""
    package = background_check.package
    
    check_mapping = {
        'criminal': ['criminal_county', 'criminal_state', 'criminal_federal'],
        'employment': ['employment_verification'],
        'education': ['education_verification'],
        'identity': ['identity_verification', 'ssn_verification'],
        'credit': ['credit_check'],
        'driving': ['driving_record'],
        'drug_test': ['drug_test'],
        'reference': ['reference_check'],
        'professional': ['professional_license'],
        'social_media': ['social_media_check'],
    }
    
    for check_category in package.included_checks:
        if check_category in check_mapping:
            for check_type in check_mapping[check_category]:
                IndividualCheck.objects.create(
                    background_check=background_check,
                    check_type=check_type,
                    status='pending'
                )
    
    # Add international checks if requested
    if background_check.international_checks:
        IndividualCheck.objects.create(
            background_check=background_check,
            check_type='criminal_international',
            status='pending'
        )

@login_required
def request_detail(request, request_id):
    """View background check request details"""
    background_check = get_object_or_404(
        BackgroundCheckRequest,
        request_id=request_id,
        recruiter=request.user.recruiter_profile
    )
    
    individual_checks = background_check.individual_checks.all().order_by('check_type')
    documents = background_check.documents.all().order_by('-uploaded_at')
    alerts = VerificationAlert.objects.filter(
        individual_check__background_check=background_check
    ).order_by('-severity', '-created_at')
    
    context = {
        'background_check': background_check,
        'individual_checks': individual_checks,
        'documents': documents,
        'alerts': alerts,
        'progress_percentage': background_check.get_progress_percentage(),
    }
    
    return render(request, 'background_verification/request_detail.html', context)

def candidate_portal(request, request_id):
    """Candidate portal for document submission and consent"""
    background_check = get_object_or_404(BackgroundCheckRequest, request_id=request_id)
    
    # Check if candidate is accessing their own background check
    if request.user.is_authenticated:
        if (request.user.user_type == 'candidate' and 
            request.user.candidate_profile != background_check.application.candidate):
            messages.error(request, 'You can only access your own background check.')
            return redirect('dashboard:home')
    
    context = {
        'background_check': background_check,
        'documents': background_check.documents.all(),
        'required_documents': get_required_documents(background_check),
    }
    
    return render(request, 'background_verification/candidate_portal.html', context)

def get_required_documents(background_check):
    """Get list of required documents based on check types"""
    required_docs = []
    
    check_types = background_check.individual_checks.values_list('check_type', flat=True)
    
    if any(check in check_types for check in ['identity_verification', 'ssn_verification']):
        required_docs.append({
            'type': 'identity',
            'name': 'Government-issued ID',
            'description': 'Driver\'s license, passport, or state ID'
        })
    
    if 'employment_verification' in check_types:
        required_docs.append({
            'type': 'employment_letter',
            'name': 'Employment Verification Letter',
            'description': 'Letter from previous employers'
        })
    
    if 'education_verification' in check_types:
        required_docs.append({
            'type': 'education_certificate',
            'name': 'Education Certificates',
            'description': 'Diplomas, transcripts, or certificates'
        })
    
    return required_docs

@csrf_exempt
def give_consent(request, request_id):
    """Handle candidate consent submission"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    background_check = get_object_or_404(BackgroundCheckRequest, request_id=request_id)
    
    if background_check.consent_given:
        return JsonResponse({'error': 'Consent already given'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        # Validate required consents
        if not data.get('consent_criminal'):
            return JsonResponse({'error': 'Criminal background check consent is required'}, status=400)
        
        if not data.get('acknowledge_rights'):
            return JsonResponse({'error': 'Rights acknowledgment is required'}, status=400)
        
        if not data.get('acknowledge_accuracy'):
            return JsonResponse({'error': 'Accuracy certification is required'}, status=400)
        
        # Update background check
        background_check.consent_given = True
        background_check.consent_given_at = timezone.now()
        background_check.consent_ip_address = get_client_ip(request)
        background_check.status = 'consent_given'
        background_check.save()
        
        # Log compliance action
        ComplianceLog.objects.create(
            background_check=background_check,
            action_type='consent_obtained',
            description='Candidate consent obtained',
            performed_by=background_check.application.candidate.user,
            ip_address=get_client_ip(request)
        )
        
        # Start background checks
        initiate_background_checks(background_check)
        
        return JsonResponse({'success': True, 'message': 'Consent recorded successfully'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def initiate_background_checks(background_check):
    """Initiate individual background checks"""
    for check in background_check.individual_checks.all():
        check.status = 'in_progress'
        check.started_at = timezone.now()
        check.save()
        
        # Here you would integrate with actual background check providers
        # For now, we'll simulate the process
        
    background_check.status = 'in_progress'
    background_check.save()

@csrf_exempt
def upload_document(request, request_id):
    """Handle document upload from candidate"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    background_check = get_object_or_404(BackgroundCheckRequest, request_id=request_id)
    
    form = DocumentUploadForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.background_check = background_check
        
        # Calculate file hash
        file_content = document.file.read()
        document.file_hash = hashlib.sha256(file_content).hexdigest()
        document.file_size = len(file_content)
        document.original_filename = document.file.name
        
        # Reset file pointer
        document.file.seek(0)
        
        document.save()
        
        # Perform AI analysis
        perform_document_analysis(document)
        
        return JsonResponse({
            'success': True,
            'message': 'Document uploaded successfully',
            'document_id': document.id
        })
    
    else:
        return JsonResponse({
            'error': 'Form validation failed',
            'errors': form.errors
        }, status=400)

def perform_document_analysis(document):
    """Perform AI analysis on uploaded document"""
    try:
        ai_verifier = DocumentVerificationAI()
        analysis_result = ai_verifier.analyze_document(
            document.file.path,
            document.document_type
        )
        
        # Update document with AI analysis results
        document.ai_extracted_data = analysis_result.get('structured_data', {})
        document.ai_authenticity_score = analysis_result.get('authenticity_score', 0)
        document.ai_quality_score = analysis_result.get('quality_score', 0)
        document.save()
        
        # Create alerts if issues found
        if analysis_result.get('authenticity_score', 0) < 70:
            VerificationAlert.objects.create(
                individual_check=document.background_check.individual_checks.first(),
                alert_type='identity_mismatch',
                severity='high',
                title='Document Authenticity Concern',
                description=f'AI analysis indicates potential authenticity issues with {document.get_document_type_display()}',
                details=analysis_result
            )
        
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Document analysis failed: {str(e)}")

@login_required
def review_document(request, document_id):
    """Review uploaded document"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    document = get_object_or_404(
        VerificationDocument,
        pk=document_id,
        background_check__recruiter=request.user.recruiter_profile
    )
    
    if request.method == 'POST':
        form = DocumentReviewForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save(commit=False)
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Document review completed'
            })
        else:
            return JsonResponse({
                'error': 'Form validation failed',
                'errors': form.errors
            }, status=400)
    
    context = {
        'document': document,
        'form': DocumentReviewForm(instance=document),
    }
    
    return render(request, 'background_verification/review_document.html', context)

@login_required
def send_document_request(request, request_id):
    """Send document request email to candidate"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    background_check = get_object_or_404(
        BackgroundCheckRequest,
        request_id=request_id,
        recruiter=request.user.recruiter_profile
    )
    
    if request.method == 'POST':
        data = json.loads(request.body)
        document_types = data.get('document_types', [])
        custom_message = data.get('message', '')
        
        # Send email
        send_document_request_email(background_check, document_types, custom_message)
        
        return JsonResponse({
            'success': True,
            'message': 'Document request sent successfully'
        })
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def send_consent_request_email(background_check):
    """Send consent request email to candidate"""
    template = VerificationTemplate.objects.filter(
        template_type='consent_request',
        is_active=True
    ).first()
    
    if not template:
        # Use default template
        subject = f"Background Check Consent Required - {background_check.application.job.title}"
        body = f"""
        Dear {background_check.application.candidate.get_full_name()},
        
        {background_check.application.job.company.name} has requested a background check as part of your application for the {background_check.application.job.title} position.
        
        Please click the link below to review the details and provide your consent:
        {settings.SITE_URL}/verification/portal/{background_check.request_id}/
        
        This background check will include: {', '.join(background_check.package.included_checks)}
        
        If you have any questions, please contact us at {background_check.recruiter.user.email}
        
        Best regards,
        {background_check.application.job.company.name} Hiring Team
        """
    else:
        subject = template.subject.format(
            candidate_name=background_check.application.candidate.get_full_name(),
            company_name=background_check.application.job.company.name,
            job_title=background_check.application.job.title
        )
        body = template.body.format(
            candidate_name=background_check.application.candidate.get_full_name(),
            company_name=background_check.application.job.company.name,
            job_title=background_check.application.job.title,
            request_id=background_check.request_id,
            portal_link=f"{settings.SITE_URL}/verification/portal/{background_check.request_id}/",
            contact_email=background_check.recruiter.user.email
        )
    
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[background_check.candidate_email],
        fail_silently=False
    )

def send_document_request_email(background_check, document_types, custom_message):
    """Send document request email to candidate"""
    subject = f"Additional Documents Required - Background Check"
    
    doc_list = '\n'.join([f"- {doc_type.replace('_', ' ').title()}" for doc_type in document_types])
    
    body = f"""
    Dear {background_check.application.candidate.get_full_name()},
    
    We need additional documents to complete your background check for the {background_check.application.job.title} position.
    
    Please upload the following documents:
    {doc_list}
    
    {custom_message}
    
    Upload documents here: {settings.SITE_URL}/verification/portal/{background_check.request_id}/
    
    Best regards,
    {background_check.application.job.company.name} Hiring Team
    """
    
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[background_check.candidate_email],
        fail_silently=False
    )

@login_required
def verification_reports(request):
    """Generate verification reports and analytics"""
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can access reports.')
        return redirect('dashboard:home')
    
    recruiter = request.user.recruiter_profile
    
    # Get date range from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    queryset = BackgroundCheckRequest.objects.filter(recruiter=recruiter)
    
    if from_date:
        queryset = queryset.filter(created_at__gte=from_date)
    if to_date:
        queryset = queryset.filter(created_at__lte=to_date)
    
    # Calculate statistics
    stats = {
        'total_checks': queryset.count(),
        'completed_checks': queryset.filter(status='completed').count(),
        'pending_checks': queryset.filter(status__in=['pending_consent', 'in_progress']).count(),
        'clear_results': queryset.filter(overall_result='clear').count(),
        'consider_results': queryset.filter(overall_result='consider').count(),
        'suspended_results': queryset.filter(overall_result='suspended').count(),
        'average_turnaround': queryset.filter(
            completed_at__isnull=False
        ).aggregate(
            avg_days=Avg('completed_at') - Avg('requested_at')
        )['avg_days'],
        'total_cost': sum(check.actual_cost for check in queryset if check.actual_cost),
    }
    
    # Recent alerts
    recent_alerts = VerificationAlert.objects.filter(
        individual_check__background_check__recruiter=recruiter
    ).order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'recent_alerts': recent_alerts,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'background_verification/reports.html', context)

class BackgroundCheckListView(LoginRequiredMixin, ListView):
    """List view for background check requests"""
    model = BackgroundCheckRequest
    template_name = 'background_verification/request_list.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.user_type != 'recruiter':
            return BackgroundCheckRequest.objects.none()
        
        queryset = BackgroundCheckRequest.objects.filter(
            recruiter=self.request.user.recruiter_profile
        ).select_related('application__candidate', 'package')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(application__candidate__first_name__icontains=search) |
                Q(application__candidate__last_name__icontains=search) |
                Q(application__job__title__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = BackgroundCheckRequest.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

@login_required
@require_POST
def bulk_action(request):
    """Handle bulk actions on background checks"""
    if request.user.user_type != 'recruiter':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    form = BulkActionForm(request.POST)
    if form.is_valid():
        action = form.cleaned_data['action']
        check_ids = form.cleaned_data['selected_checks']
        
        checks = BackgroundCheckRequest.objects.filter(
            id__in=check_ids,
            recruiter=request.user.recruiter_profile
        )
        
        if action == 'send_reminder':
            for check in checks:
                send_reminder_email(check)
            message = f'Reminder emails sent to {checks.count()} candidates'
            
        elif action == 'cancel':
            checks.update(status='cancelled')
            message = f'{checks.count()} background checks cancelled'
            
        elif action == 'expedite':
            checks.update(rush_processing=True)
            message = f'{checks.count()} background checks expedited'
            
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        return JsonResponse({'success': True, 'message': message})
    
    return JsonResponse({'error': 'Form validation failed', 'errors': form.errors}, status=400)

def send_reminder_email(background_check):
    """Send reminder email to candidate"""
    subject = f"Reminder: Background Check Action Required"
    body = f"""
    Dear {background_check.application.candidate.get_full_name()},
    
    This is a reminder that we are still waiting for your action on the background check for the {background_check.application.job.title} position.
    
    Please visit: {settings.SITE_URL}/verification/portal/{background_check.request_id}/
    
    If you have any questions, please contact us.
    
    Best regards,
    {background_check.application.job.company.name} Hiring Team
    """
    
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[background_check.candidate_email],
        fail_silently=False
    )
