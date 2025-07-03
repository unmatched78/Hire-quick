from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='candidate')
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"

    def get_profile(self):
        """Get the user's profile based on user type"""
        if self.user_type == 'candidate':
            return getattr(self, 'candidate_profile', None)
        elif self.user_type == 'recruiter':
            return getattr(self, 'recruiter_profile', None)
        return None

    def get_full_name(self):
        """Get full name from profile or fallback to username"""
        profile = self.get_profile()
        if profile and hasattr(profile, 'get_full_name'):
            return profile.get_full_name()
        return self.get_username()

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True)
    summary = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    current_title = models.CharField(max_length=200, blank=True)
    salary_expectation = models.PositiveIntegerField(null=True, blank=True)
    availability = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    profile_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user.email})"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email.split('@')[0]
    
    def get_absolute_url(self):
        return reverse('accounts:candidate_profile', kwargs={'pk': self.pk})
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        fields = [
            self.first_name, self.last_name, self.location, self.summary,
            self.current_title, self.skills, self.experience_years
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)

class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='recruiters', null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    profile_completed = models.BooleanField(default=False)
    
    def __str__(self):
        company_name = self.company.name if self.company else "No Company"
        return f"{self.get_full_name()} - {company_name}"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email.split('@')[0]
    
    def get_absolute_url(self):
        return reverse('accounts:recruiter_profile', kwargs={'pk': self.pk})

# Signal handlers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created"""
    if created:
        if instance.user_type == 'candidate':
            CandidateProfile.objects.create(user=instance)
        elif instance.user_type == 'recruiter':
            RecruiterProfile.objects.create(user=instance)

@receiver(user_signed_up)
def user_signed_up_handler(request, user, **kwargs):
    """Handle user signup from social accounts"""
    # Extract additional info from social account if available
    if hasattr(user, 'socialaccount_set'):
        social_account = user.socialaccount_set.first()
        if social_account:
            extra_data = social_account.extra_data
            profile = user.get_profile()
            
            if profile and isinstance(profile, (CandidateProfile, RecruiterProfile)):
                # Extract name from social account
                if 'first_name' in extra_data:
                    profile.first_name = extra_data['first_name']
                if 'last_name' in extra_data:
                    profile.last_name = extra_data['last_name']
                if 'name' in extra_data and not (profile.first_name and profile.last_name):
                    name_parts = extra_data['name'].split(' ', 1)
                    profile.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        profile.last_name = name_parts[1]
                
                # Extract LinkedIn URL for candidates
                if isinstance(profile, CandidateProfile) and social_account.provider == 'linkedin_oauth2':
                    if 'publicProfileUrl' in extra_data:
                        profile.linkedin_url = extra_data['publicProfileUrl']
                
                # Extract GitHub URL for candidates
                if isinstance(profile, CandidateProfile) and social_account.provider == 'github':
                    if 'html_url' in extra_data:
                        profile.github_url = extra_data['html_url']
                
                profile.save()
