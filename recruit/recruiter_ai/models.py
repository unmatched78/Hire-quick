from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class JobGenerationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    recruiter = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='job_generation_requests')
    job_title = models.CharField(max_length=200)
    company_description = models.TextField(blank=True)
    requirements_input = models.TextField(help_text="Brief description of what you're looking for")
    industry = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=50, choices=[
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
    ], default='mid')
    employment_type = models.CharField(max_length=20, choices=[
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ], default='full-time')
    remote_option = models.CharField(max_length=20, choices=[
        ('onsite', 'On-site Only'),
        ('remote', 'Remote Only'),
        ('hybrid', 'Hybrid'),
    ], default='hybrid')
    
    # Generated content
    generated_description = models.TextField(blank=True)
    generated_requirements = models.JSONField(default=list, blank=True)
    generated_benefits = models.JSONField(default=list, blank=True)
    generated_skills = models.JSONField(default=list, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Whether the recruiter used this to create a job
    job_created = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job Generation: {self.job_title} for {self.recruiter.company.name}"

class InterviewSchedule(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('phone', 'Phone Interview'),
        ('video', 'Video Interview'),
        ('in-person', 'In-Person Interview'),
        ('technical', 'Technical Interview'),
        ('panel', 'Panel Interview'),
        ('final', 'Final Interview'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no_show', 'No Show'),
    ]
    
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='scheduled_interviews')
    interviewer = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='scheduled_interviews')
    
    # Interview details
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES, default='video')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Location/Meeting details
    location = models.CharField(max_length=200, blank=True, help_text="Physical address or meeting room")
    meeting_link = models.URLField(blank=True, help_text="Video call link")
    meeting_id = models.CharField(max_length=100, blank=True, help_text="Meeting ID/Password")
    
    # Additional information
    agenda = models.TextField(blank=True, help_text="Interview agenda or topics to cover")
    preparation_notes = models.TextField(blank=True, help_text="Notes for the candidate")
    internal_notes = models.TextField(blank=True, help_text="Internal notes for the interviewer")
    
    # Status and notifications
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    candidate_notified = models.BooleanField(default=False)
    interviewer_notified = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    
    # Feedback after interview
    feedback = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="Rating from 1-5")
    recommendation = models.CharField(max_length=20, choices=[
        ('hire', 'Recommend to Hire'),
        ('maybe', 'Maybe'),
        ('no_hire', 'Do Not Hire'),
    ], blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        unique_together = ['application', 'scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f"{self.get_interview_type_display()} - {self.application.candidate.get_full_name()} on {self.scheduled_date}"
    
    @property
    def scheduled_datetime(self):
        return timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
    
    def is_upcoming(self):
        return self.scheduled_datetime > timezone.now()
    
    def is_today(self):
        return self.scheduled_date == timezone.now().date()

class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('interview', 'Interview'),
        ('meeting', 'Meeting'),
        ('deadline', 'Deadline'),
        ('reminder', 'Reminder'),
    ]
    
    recruiter = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='meeting')
    
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    
    # Optional links to other models
    interview_schedule = models.OneToOneField(InterviewSchedule, on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, null=True, blank=True)
    
    # Notification settings
    email_reminder = models.BooleanField(default=True)
    reminder_minutes_before = models.PositiveIntegerField(default=30, help_text="Minutes before event to send reminder")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.start_date} {self.start_time}"
