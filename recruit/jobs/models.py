from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='jobs')
    recruiter = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='posted_jobs')
    description = models.TextField()
    requirements = models.JSONField(default=list, blank=True, help_text='List of required skills/qualifications')
    preferred_skills = models.JSONField(default=list, blank=True, help_text='List of preferred skills')
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full-time')
    remote_ok = models.BooleanField(default=False)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    experience_min = models.PositiveIntegerField(default=0, help_text='Minimum years of experience')
    experience_max = models.PositiveIntegerField(null=True, blank=True, help_text='Maximum years of experience')
    education_required = models.CharField(max_length=100, blank=True)
    benefits = models.JSONField(default=list, blank=True, help_text='List of benefits offered')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # New field for custom application requirements
    has_custom_application_form = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})
    
    def get_salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        return "Salary not specified"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def days_since_posted(self):
        return (timezone.now() - self.created_at).days
    
    def get_applications_count(self):
        return self.applications.count()
    
    def save(self, *args, **kwargs):
        # Set default expiry date if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

class ApplicationFormField(models.Model):
    FIELD_TYPE_CHOICES = [
        ('text', 'Short Text'),
        ('textarea', 'Long Text'),
        ('email', 'Email'),
        ('phone', 'Phone Number'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('file', 'File Upload'),
        ('resume', 'Resume Upload'),
        ('cover_letter', 'Cover Letter'),
        ('video', 'Video Upload'),
        ('audio', 'Audio Upload'),
        ('url', 'Website/Portfolio URL'),
        ('select', 'Dropdown Selection'),
        ('radio', 'Multiple Choice'),
        ('checkbox', 'Checkboxes'),
        ('boolean', 'Yes/No Question'),
        ('rating', 'Rating Scale'),
        ('linkedin', 'LinkedIn Profile'),
        ('github', 'GitHub Profile'),
        ('portfolio', 'Portfolio Upload'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='application_form_fields')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    label = models.CharField(max_length=200, help_text='Question or field label')
    help_text = models.TextField(blank=True, help_text='Additional instructions for applicants')
    placeholder = models.CharField(max_length=200, blank=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # For select, radio, checkbox fields
    choices = models.JSONField(default=list, blank=True, help_text='Options for select/radio/checkbox fields')
    
    # File upload constraints
    max_file_size_mb = models.PositiveIntegerField(default=10, help_text='Maximum file size in MB')
    allowed_file_types = models.JSONField(
        default=list, 
        blank=True, 
        help_text='Allowed file extensions (e.g., ["pdf", "doc", "docx"])'
    )
    
    # Video/Audio constraints
    max_duration_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text='Maximum duration for video/audio in minutes'
    )
    
    # Rating scale settings
    min_rating = models.PositiveIntegerField(default=1, help_text='Minimum rating value')
    max_rating = models.PositiveIntegerField(default=5, help_text='Maximum rating value')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ('job', 'order')
    
    def __str__(self):
        return f"{self.job.title} - {self.label}"
    
    def get_field_widget_attrs(self):
        """Get HTML attributes for form field widget"""
        attrs = {'class': 'form-control'}
        
        if self.placeholder:
            attrs['placeholder'] = self.placeholder
        
        if self.field_type == 'file':
            if self.allowed_file_types:
                attrs['accept'] = ','.join([f'.{ext}' for ext in self.allowed_file_types])
        
        elif self.field_type == 'video':
            attrs['accept'] = 'video/*'
            attrs['class'] = 'form-control video-upload'
        
        elif self.field_type == 'audio':
            attrs['accept'] = 'audio/*'
            attrs['class'] = 'form-control audio-upload'
        
        elif self.field_type == 'textarea':
            attrs['rows'] = 4
        
        return attrs

class SavedJob(models.Model):
    candidate = models.ForeignKey('accounts.CandidateProfile', on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('candidate', 'job')
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} saved {self.job.title}"
