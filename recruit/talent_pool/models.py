from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

class TalentPool(models.Model):
    POOL_TYPE_CHOICES = [
        ('general', 'General Pool'),
        ('role_specific', 'Role Specific'),
        ('skill_based', 'Skill Based'),
        ('location_based', 'Location Based'),
        ('pipeline', 'Pipeline Pool'),
        ('alumni', 'Alumni Pool'),
        ('referral', 'Referral Pool'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pool_type = models.CharField(max_length=20, choices=POOL_TYPE_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Pool criteria
    required_skills = models.JSONField(default=list, blank=True)
    preferred_skills = models.JSONField(default=list, blank=True)
    min_experience = models.IntegerField(default=0)
    max_experience = models.IntegerField(null=True, blank=True)
    locations = models.JSONField(default=list, blank=True)
    education_requirements = models.JSONField(default=list, blank=True)
    
    # Relationships
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='talent_pools')
    created_by = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    def get_absolute_url(self):
        return reverse('talent_pool:detail', kwargs={'pk': self.pk})
    
    def get_candidate_count(self):
        return self.candidates.count()
    
    def get_active_candidate_count(self):
        return self.candidates.filter(status='active').count()
    
    def get_recent_additions_count(self):
        return self.candidates.filter(
            added_at__gte=timezone.now() - timedelta(days=7)
        ).count()

class TalentPoolCandidate(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('hired', 'Hired'),
        ('inactive', 'Inactive'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.CASCADE, related_name='candidates')
    candidate = models.ForeignKey('accounts.CandidateProfile', on_delete=models.CASCADE, related_name='talent_pools')
    
    # Match information
    match_score = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Tracking
    added_by = models.ForeignKey('accounts.RecruiterProfile', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['talent_pool', 'candidate']
        ordering = ['-match_score', '-added_at']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} in {self.talent_pool.name}"

class JobMatch(models.Model):
    MATCH_TYPE_CHOICES = [
        ('auto', 'Automatic'),
        ('manual', 'Manual'),
        ('ai_recommended', 'AI Recommended'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('applied', 'Applied'),
        ('expired', 'Expired'),
    ]
    
    candidate = models.ForeignKey('accounts.CandidateProfile', on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='candidate_matches')
    
    # Match details
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, default='auto')
    overall_score = models.FloatField()
    skill_score = models.FloatField()
    experience_score = models.FloatField()
    location_score = models.FloatField()
    education_score = models.FloatField()
    
    # Match analysis
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    match_reasons = models.JSONField(default=list)
    ai_recommendation = models.TextField()
    fit_analysis = models.JSONField(default=dict)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['candidate', 'job']
        ordering = ['-overall_score', '-created_at']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.job.title} ({self.overall_score}%)"
    
    def get_absolute_url(self):
        return reverse('talent_pool:job_match_detail', kwargs={'pk': self.pk})
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def get_match_grade(self):
        if self.overall_score >= 90:
            return 'A+'
        elif self.overall_score >= 85:
            return 'A'
        elif self.overall_score >= 80:
            return 'B+'
        elif self.overall_score >= 75:
            return 'B'
        elif self.overall_score >= 70:
            return 'C+'
        elif self.overall_score >= 65:
            return 'C'
        else:
            return 'D'

class CandidatePreferences(models.Model):
    REMOTE_PREFERENCES = [
        ('required', 'Remote Required'),
        ('preferred', 'Remote Preferred'),
        ('hybrid', 'Hybrid OK'),
        ('onsite', 'Onsite Only'),
    ]
    
    
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    
    candidate = models.OneToOneField('accounts.CandidateProfile', on_delete=models.CASCADE, related_name='job_preferences')
    
    # Job preferences
    job_types = models.JSONField(default=list, blank=True)
    preferred_roles = models.JSONField(default=list, blank=True)
    industries = models.JSONField(default=list, blank=True)
    company_sizes = models.JSONField(default=list, blank=True)
    
    # Location preferences
    preferred_locations = models.JSONField(default=list, blank=True)
    STATUS_CHOICES=models.CharField(max_length=20, choices=REMOTE_PREFERENCES, default='hybrid')
    remote_preference = models.CharField(max_length=20, choices=REMOTE_PREFERENCES, default='hybrid')
    willing_to_relocate = models.BooleanField(default=False)
    
    # Salary preferences
    min_salary = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)
    salary_negotiable = models.BooleanField(default=True)
    
    # Availability
    available_from = models.DateField(null=True, blank=True)
    notice_period_weeks = models.IntegerField(default=2)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    match_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='weekly')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.candidate.get_full_name()}"

class MatchingActivity(models.Model):
    ACTION_CHOICES = [
        ('pool_added', 'Added to Pool'),
        ('pool_removed', 'Removed from Pool'),
        ('match_created', 'Match Created'),
        ('match_viewed', 'Match Viewed'),
        ('match_interested', 'Expressed Interest'),
        ('match_not_interested', 'Not Interested'),
        ('match_applied', 'Applied'),
        ('preferences_updated', 'Preferences Updated'),
        ('contacted', 'Contacted by Recruiter'),
    ]
    
    candidate = models.ForeignKey('accounts.CandidateProfile', on_delete=models.CASCADE, related_name='matching_activities')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, null=True, blank=True)
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.CASCADE, null=True, blank=True)
    
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.get_action_display()}"
