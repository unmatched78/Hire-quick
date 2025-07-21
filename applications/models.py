from django.db import models
from django.urls import reverse
import json

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey('accounts.CandidateProfile', on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    
    # Traditional fields (still supported for backward compatibility)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True)
    
    # Dynamic form responses
    form_responses = models.JSONField(default=dict, blank=True, help_text='Responses to custom application form fields')
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text='Internal notes from recruiters')
    
    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.job.title}"
    
    def get_absolute_url(self):
        return reverse('applications:detail', kwargs={'pk': self.pk})
    
    def get_status_badge_class(self):
        status_classes = {
            'applied': 'bg-primary',
            'screening': 'bg-warning',
            'interview': 'bg-info',
            'offer': 'bg-success',
            'hired': 'bg-success',
            'rejected': 'bg-danger',
            'withdrawn': 'bg-secondary',
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def get_form_response(self, field_id):
        """Get response for a specific form field"""
        return self.form_responses.get(str(field_id), '')
    
    def set_form_response(self, field_id, value):
        """Set response for a specific form field"""
        if not self.form_responses:
            self.form_responses = {}
        self.form_responses[str(field_id)] = value
    
    def get_uploaded_files(self):
        """Get all uploaded files from form responses"""
        files = []
        for field_id, response in self.form_responses.items():
            if isinstance(response, dict) and 'file_path' in response:
                files.append({
                    'field_id': field_id,
                    'file_path': response['file_path'],
                    'original_name': response.get('original_name', ''),
                    'file_type': response.get('file_type', ''),
                })
        return files

class ParsedResume(models.Model):
    """Store parsed resume data"""
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='parsed_resume')
    
    # Contact Information
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Skills (stored as JSON)
    skills_data = models.JSONField(default=dict, blank=True, help_text='Categorized skills extracted from resume')
    
    # Experience
    total_experience_years = models.FloatField(default=0.0)
    experience_data = models.JSONField(default=list, blank=True, help_text='Work experience details')
    
    # Education
    education_data = models.JSONField(default=list, blank=True, help_text='Education details')
    
    # Certifications
    certifications_data = models.JSONField(default=list, blank=True, help_text='Certifications')
    
    # Languages
    languages_data = models.JSONField(default=list, blank=True, help_text='Languages and proficiency')
    
    # AI Analysis
    ai_score = models.FloatField(null=True, blank=True, help_text='AI-generated resume score (1-10)')
    ai_strengths = models.JSONField(default=list, blank=True, help_text='AI-identified strengths')
    ai_improvements = models.JSONField(default=list, blank=True, help_text='AI-suggested improvements')
    ai_suitable_roles = models.JSONField(default=list, blank=True, help_text='AI-suggested suitable roles')
    career_level = models.CharField(max_length=20, blank=True, help_text='Junior/Mid/Senior')
    
    # Job Matching
    skill_match_percentage = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    
    # Metadata
    raw_text = models.TextField(blank=True, help_text='Raw extracted text from resume')
    parsing_errors = models.JSONField(default=list, blank=True, help_text='Any errors during parsing')
    parsed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-parsed_at']
    
    def __str__(self):
        return f"Parsed Resume - {self.application}"
    
    def get_all_skills(self):
        """Get flattened list of all skills"""
        all_skills = []
        for category, skills in self.skills_data.items():
            if isinstance(skills, list):
                all_skills.extend(skills)
        return all_skills
    
    def get_skills_by_category(self):
        """Get skills organized by category"""
        return self.skills_data
    
    def get_experience_summary(self):
        """Get summary of work experience"""
        if not self.experience_data:
            return "No experience data available"
        
        companies = [exp.get('company', 'Unknown') for exp in self.experience_data if exp.get('company')]
        roles = [exp.get('job_title', 'Unknown') for exp in self.experience_data if exp.get('job_title')]
        
        return {
            'total_positions': len(self.experience_data),
            'companies': list(set(companies)),
            'roles': list(set(roles)),
            'total_years': self.total_experience_years
        }
    
    def get_education_summary(self):
        """Get summary of education"""
        if not self.education_data:
            return "No education data available"
        
        degrees = [edu.get('degree', 'Unknown') for edu in self.education_data if edu.get('degree')]
        institutions = [edu.get('institution', 'Unknown') for edu in self.education_data if edu.get('institution')]
        
        return {
            'total_degrees': len(self.education_data),
            'degrees': degrees,
            'institutions': institutions
        }

class ApplicationFile(models.Model):
    """Store files uploaded through dynamic application forms"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='uploaded_files')
    form_field = models.ForeignKey('jobs.ApplicationFormField', on_delete=models.CASCADE)
    file = models.FileField(upload_to='application_files/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # in bytes
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Resume parsing status
    is_resume = models.BooleanField(default=False)
    parsing_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    parsing_error = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.application} - {self.form_field.label} - {self.original_filename}"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def is_image(self):
        return self.content_type.startswith('image/')
    
    def is_video(self):
        return self.content_type.startswith('video/')
    
    def is_audio(self):
        return self.content_type.startswith('audio/')
    
    def is_pdf(self):
        return self.content_type == 'application/pdf'
    
    def is_document(self):
        return self.content_type in [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]

class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('phone', 'Phone Interview'),
        ('video', 'Video Interview'),
        ('in-person', 'In-Person Interview'),
        ('technical', 'Technical Interview'),
        ('final', 'Final Interview'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='conducted_interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES, default='video')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=200, blank=True, help_text='Physical location or meeting link')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    feedback = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, help_text='Rating from 1-5')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_at']
    
    def __str__(self):
        return f"{self.get_interview_type_display()} - {self.application}"
    
    def get_absolute_url(self):
        return reverse('applications:interview_detail', kwargs={'pk': self.pk})
