from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
import uuid
import json
from datetime import timedelta

User = get_user_model()

class VerificationProvider(models.Model):
    """Third-party verification service providers"""
    PROVIDER_TYPES = [
        ('criminal', 'Criminal Background'),
        ('employment', 'Employment Verification'),
        ('education', 'Education Verification'),
        ('identity', 'Identity Verification'),
        ('credit', 'Credit Check'),
        ('driving', 'Driving Record'),
        ('drug_test', 'Drug Testing'),
        ('reference', 'Reference Check'),
        ('social_media', 'Social Media Check'),
        ('international', 'International Background'),
    ]
    
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    api_endpoint = models.URLField(blank=True)
    api_key_field = models.CharField(max_length=100, blank=True)
    supported_countries = models.JSONField(default=list, help_text="List of ISO country codes")
    is_active = models.BooleanField(default=True)
    average_turnaround_hours = models.PositiveIntegerField(default=24)
    cost_per_check = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_provider_type_display()}"

class BackgroundCheckPackage(models.Model):
    """Predefined packages of background checks"""
    PACKAGE_TYPES = [
        ('basic', 'Basic Package'),
        ('standard', 'Standard Package'),
        ('comprehensive', 'Comprehensive Package'),
        ('executive', 'Executive Package'),
        ('custom', 'Custom Package'),
    ]
    
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES)
    description = models.TextField()
    included_checks = models.JSONField(default=list, help_text="List of check types included")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_turnaround_days = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    
    # Compliance settings
    gdpr_compliant = models.BooleanField(default=True)
    fcra_compliant = models.BooleanField(default=True)
    supported_countries = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['package_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_package_type_display()})"

class BackgroundCheckRequest(models.Model):
    """Main background check request"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_consent', 'Pending Candidate Consent'),
        ('consent_given', 'Consent Given'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('normal', 'Normal Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ]
    
    # Unique identifier for tracking
    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Related models
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='background_checks')
    recruiter = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='background_check_requests')
    package = models.ForeignKey(BackgroundCheckPackage, on_delete=models.CASCADE)
    
    # Request details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Candidate information
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=20, blank=True)
    candidate_address = models.TextField()
    candidate_country = models.CharField(max_length=3, help_text="ISO country code")
    candidate_ssn_last4 = models.CharField(max_length=4, blank=True, help_text="Last 4 digits of SSN")
    candidate_date_of_birth = models.DateField(null=True, blank=True)
    
    # Consent and legal
    consent_given = models.BooleanField(default=False)
    consent_given_at = models.DateTimeField(null=True, blank=True)
    consent_ip_address = models.GenericIPAddressField(null=True, blank=True)
    legal_disclosure_sent = models.BooleanField(default=False)
    
    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    overall_result = models.CharField(max_length=20, choices=[
        ('clear', 'Clear'),
        ('consider', 'Consider'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    ], blank=True)
    
    # Costs and billing
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additional settings
    rush_processing = models.BooleanField(default=False)
    international_checks = models.BooleanField(default=False)
    custom_instructions = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['recruiter', 'status']),
        ]
    
    def __str__(self):
        return f"Background Check #{self.request_id.hex[:8]} - {self.application.candidate.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('background_verification:request_detail', kwargs={'request_id': self.request_id})
    
    def is_expired(self):
        if self.due_date:
            return timezone.now() > self.due_date
        return False
    
    def get_progress_percentage(self):
        total_checks = self.individual_checks.count()
        if total_checks == 0:
            return 0
        completed_checks = self.individual_checks.filter(status='completed').count()
        return int((completed_checks / total_checks) * 100)

class IndividualCheck(models.Model):
    """Individual verification checks within a background check request"""
    CHECK_TYPES = [
        ('criminal_county', 'County Criminal Search'),
        ('criminal_state', 'State Criminal Search'),
        ('criminal_federal', 'Federal Criminal Search'),
        ('criminal_international', 'International Criminal Search'),
        ('employment_verification', 'Employment Verification'),
        ('education_verification', 'Education Verification'),
        ('identity_verification', 'Identity Verification'),
        ('ssn_verification', 'SSN Verification'),
        ('address_verification', 'Address Verification'),
        ('credit_check', 'Credit Check'),
        ('driving_record', 'Driving Record'),
        ('drug_test', 'Drug Test'),
        ('reference_check', 'Reference Check'),
        ('professional_license', 'Professional License Verification'),
        ('social_media_check', 'Social Media Check'),
        ('sex_offender_registry', 'Sex Offender Registry'),
        ('terrorist_watch_list', 'Terrorist Watch List'),
        ('global_sanctions', 'Global Sanctions Check'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('disputed', 'Disputed'),
        ('unable_to_verify', 'Unable to Verify'),
    ]
    
    RESULT_CHOICES = [
        ('clear', 'Clear'),
        ('consider', 'Consider'),
        ('suspended', 'Suspended'),
        ('unable_to_verify', 'Unable to Verify'),
    ]
    
    background_check = models.ForeignKey(BackgroundCheckRequest, on_delete=models.CASCADE, related_name='individual_checks')
    check_type = models.CharField(max_length=30, choices=CHECK_TYPES)
    provider = models.ForeignKey(VerificationProvider, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status and results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, blank=True)
    
    # Check-specific data
    search_parameters = models.JSONField(default=dict, help_text="Parameters used for this check")
    raw_results = models.JSONField(default=dict, help_text="Raw results from provider")
    processed_results = models.JSONField(default=dict, help_text="Processed and formatted results")
    
    # AI Analysis
    ai_analysis = models.TextField(blank=True, help_text="AI-powered analysis of results")
    risk_score = models.PositiveIntegerField(null=True, blank=True, help_text="Risk score 0-100")
    confidence_score = models.PositiveIntegerField(null=True, blank=True, help_text="Confidence score 0-100")
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Cost
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Additional information
    notes = models.TextField(blank=True)
    requires_manual_review = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        unique_together = ['background_check', 'check_type']
    
    def __str__(self):
        return f"{self.get_check_type_display()} - {self.background_check.request_id.hex[:8]}"
    
    def get_turnaround_time(self):
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

class VerificationDocument(models.Model):
    """Documents submitted by candidates for verification"""
    DOCUMENT_TYPES = [
        ('identity', 'Identity Document'),
        ('address_proof', 'Address Proof'),
        ('education_certificate', 'Education Certificate'),
        ('employment_letter', 'Employment Letter'),
        ('professional_license', 'Professional License'),
        ('driving_license', 'Driving License'),
        ('passport', 'Passport'),
        ('visa', 'Visa/Work Permit'),
        ('other', 'Other Document'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('requires_resubmission', 'Requires Resubmission'),
    ]
    
    background_check = models.ForeignKey(BackgroundCheckRequest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    
    # File information
    file = models.FileField(upload_to='verification_documents/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_hash = models.CharField(max_length=64, help_text="SHA-256 hash for integrity")
    
    # Document details
    document_number = models.CharField(max_length=100, blank=True)
    issuing_authority = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    country_issued = models.CharField(max_length=3, blank=True, help_text="ISO country code")
    
    # Verification status
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # AI Analysis
    ai_extracted_data = models.JSONField(default=dict, help_text="Data extracted by AI")
    ai_authenticity_score = models.PositiveIntegerField(null=True, blank=True, help_text="Authenticity score 0-100")
    ai_quality_score = models.PositiveIntegerField(null=True, blank=True, help_text="Document quality score 0-100")
    
    # Review notes
    review_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.background_check.request_id.hex[:8]}"
    
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

class VerificationAlert(models.Model):
    """Alerts and findings from background checks"""
    ALERT_TYPES = [
        ('criminal_record', 'Criminal Record Found'),
        ('employment_discrepancy', 'Employment Discrepancy'),
        ('education_discrepancy', 'Education Discrepancy'),
        ('identity_mismatch', 'Identity Mismatch'),
        ('address_mismatch', 'Address Mismatch'),
        ('credit_issue', 'Credit Issue'),
        ('driving_violation', 'Driving Violation'),
        ('professional_license_issue', 'Professional License Issue'),
        ('reference_concern', 'Reference Concern'),
        ('social_media_concern', 'Social Media Concern'),
        ('sanctions_match', 'Sanctions List Match'),
        ('watch_list_match', 'Watch List Match'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    individual_check = models.ForeignKey(IndividualCheck, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    
    # Alert details
    title = models.CharField(max_length=200)
    description = models.TextField()
    details = models.JSONField(default=dict, help_text="Structured alert details")
    
    # Source information
    source = models.CharField(max_length=100, help_text="Source of the alert")
    source_date = models.DateField(null=True, blank=True)
    jurisdiction = models.CharField(max_length=100, blank=True)
    
    # Review status
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Dispute information
    disputed = models.BooleanField(default=False)
    dispute_reason = models.TextField(blank=True)
    dispute_resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"

class ComplianceLog(models.Model):
    """Compliance and audit log for background checks"""
    ACTION_TYPES = [
        ('request_created', 'Background Check Request Created'),
        ('consent_obtained', 'Candidate Consent Obtained'),
        ('check_initiated', 'Individual Check Initiated'),
        ('results_received', 'Results Received'),
        ('manual_review', 'Manual Review Conducted'),
        ('dispute_filed', 'Dispute Filed'),
        ('data_retention', 'Data Retention Action'),
        ('data_deletion', 'Data Deletion'),
        ('access_granted', 'Access Granted'),
        ('report_generated', 'Report Generated'),
    ]
    
    background_check = models.ForeignKey(BackgroundCheckRequest, on_delete=models.CASCADE, related_name='compliance_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    # Action details
    description = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Compliance metadata
    gdpr_basis = models.CharField(max_length=100, blank=True, help_text="GDPR legal basis")
    fcra_compliance = models.BooleanField(default=True)
    data_retention_date = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.created_at}"

class VerificationTemplate(models.Model):
    """Email templates for verification requests"""
    TEMPLATE_TYPES = [
        ('consent_request', 'Consent Request'),
        ('document_request', 'Document Request'),
        ('status_update', 'Status Update'),
        ('completion_notice', 'Completion Notice'),
        ('dispute_notice', 'Dispute Notice'),
        ('reminder', 'Reminder'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    body = models.TextField(help_text="Use {{variable}} for dynamic content")
    
    # Customization
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Compliance
    includes_legal_disclosure = models.BooleanField(default=False)
    gdpr_compliant = models.BooleanField(default=True)
    fcra_compliant = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
