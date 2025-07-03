from django import forms
from django.core.exceptions import ValidationError
from .models import (
    BackgroundCheckRequest, BackgroundCheckPackage, VerificationDocument,
    VerificationTemplate, IndividualCheck
)
import pycountry

class BackgroundCheckRequestForm(forms.ModelForm):
    """Form for creating background check requests"""
    
    # Additional fields for candidate information
    candidate_first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    candidate_last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = BackgroundCheckRequest
        fields = [
            'package', 'priority', 'candidate_email', 'candidate_phone',
            'candidate_address', 'candidate_country', 'candidate_ssn_last4',
            'candidate_date_of_birth', 'rush_processing', 'international_checks',
            'custom_instructions'
        ]
        widgets = {
            'package': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'candidate_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'candidate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'candidate_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'candidate_country': forms.Select(attrs={'class': 'form-control'}),
            'candidate_ssn_last4': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 4, 'placeholder': 'Last 4 digits'}),
            'candidate_date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'custom_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate country choices
        country_choices = [('', 'Select Country')]
        for country in pycountry.countries:
            country_choices.append((country.alpha_3, country.name))
        
        self.fields['candidate_country'].choices = country_choices
        
        # Filter active packages
        self.fields['package'].queryset = BackgroundCheckPackage.objects.filter(is_active=True)
    
    def clean_candidate_ssn_last4(self):
        ssn_last4 = self.cleaned_data.get('candidate_ssn_last4')
        if ssn_last4 and not ssn_last4.isdigit():
            raise ValidationError("SSN last 4 digits must be numeric")
        return ssn_last4

class DocumentUploadForm(forms.ModelForm):
    """Form for candidates to upload verification documents"""
    
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'file', 'document_number', 'issuing_authority', 
                 'issue_date', 'expiry_date', 'country_issued']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'country_issued': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate country choices
        country_choices = [('', 'Select Country')]
        for country in pycountry.countries:
            country_choices.append((country.alpha_3, country.name))
        
        self.fields['country_issued'].choices = country_choices
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB")
            
            # Check file type
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
            if file.content_type not in allowed_types:
                raise ValidationError("Only PDF, JPEG, and PNG files are allowed")
        
        return file

class ConsentForm(forms.Form):
    """Form for candidate consent to background check"""
    
    consent_criminal = forms.BooleanField(
        required=True,
        label="I consent to criminal background checks",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    consent_employment = forms.BooleanField(
        required=False,
        label="I consent to employment verification",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    consent_education = forms.BooleanField(
        required=False,
        label="I consent to education verification",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    consent_credit = forms.BooleanField(
        required=False,
        label="I consent to credit checks (if applicable)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    consent_driving = forms.BooleanField(
        required=False,
        label="I consent to driving record checks (if applicable)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    consent_references = forms.BooleanField(
        required=False,
        label="I consent to reference checks",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    acknowledge_rights = forms.BooleanField(
        required=True,
        label="I acknowledge that I have read and understand my rights regarding background checks",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    acknowledge_accuracy = forms.BooleanField(
        required=True,
        label="I certify that all information provided is accurate and complete",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class PackageSelectionForm(forms.Form):
    """Form for selecting background check package"""
    
    package = forms.ModelChoiceField(
        queryset=BackgroundCheckPackage.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    
    rush_processing = forms.BooleanField(
        required=False,
        label="Rush Processing (+50% fee)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    international_checks = forms.BooleanField(
        required=False,
        label="Include International Checks",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class DocumentReviewForm(forms.ModelForm):
    """Form for reviewing uploaded documents"""
    
    class Meta:
        model = VerificationDocument
        fields = ['status', 'review_notes', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'rejected' and not rejection_reason:
            raise ValidationError("Rejection reason is required when rejecting a document")
        
        return cleaned_data

class CheckStatusUpdateForm(forms.ModelForm):
    """Form for updating individual check status"""
    
    class Meta:
        model = IndividualCheck
        fields = ['status', 'result', 'notes', 'requires_manual_review']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'result': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requires_manual_review': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmailTemplateForm(forms.ModelForm):
    """Form for creating/editing email templates"""
    
    class Meta:
        model = VerificationTemplate
        fields = ['name', 'template_type', 'subject', 'body', 'includes_legal_disclosure']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'includes_legal_disclosure': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].help_text = """
        Available variables:
        {{candidate_name}}, {{company_name}}, {{job_title}}, {{request_id}},
        {{due_date}}, {{portal_link}}, {{contact_email}}
        """

class BulkActionForm(forms.Form):
    """Form for bulk actions on background checks"""
    
    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('send_reminder', 'Send Reminder'),
        ('cancel', 'Cancel Checks'),
        ('expedite', 'Expedite Processing'),
        ('export', 'Export Results'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    selected_checks = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_selected_checks(self):
        selected = self.cleaned_data.get('selected_checks')
        if not selected:
            raise ValidationError("No checks selected")
        
        try:
            check_ids = [int(id) for id in selected.split(',')]
            return check_ids
        except ValueError:
            raise ValidationError("Invalid check IDs")
