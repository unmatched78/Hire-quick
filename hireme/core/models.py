from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model with user types
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('company_rep', 'Company Representative'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

# JobSeeker profile linked to User
class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    preferences = models.JSONField(default=dict, blank=True)

# Company profile linked to User
class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    culture = models.TextField(blank=True)

# Job postings
class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    posted_by = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)

# Job applications
class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('interviewed', 'Interviewed'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    date_applied = models.DateTimeField(auto_now_add=True)

# Company reviews by job seekers
class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)