from django.db import models
from django.urls import reverse

class Company(models.Model):
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-1000', '201-1000 employees'),
        ('1000+', '1000+ employees'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    location = models.CharField(max_length=200, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('companies:detail', kwargs={'pk': self.pk})
    
    def get_active_jobs_count(self):
        return self.jobs.filter(status='active').count()
