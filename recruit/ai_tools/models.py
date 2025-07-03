from django.db import models
from django.contrib.auth import get_user_model
from pydantic import BaseModel, Field
from typing import List, Optional
import json

User = get_user_model()

class CVGenerationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cv_requests')
    job_url = models.URLField()
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Generated files
    cv_pdf = models.FileField(upload_to='generated_cvs/', blank=True)
    cv_jpg = models.ImageField(upload_to='generated_cvs/', blank=True)
    cover_letter_pdf = models.FileField(upload_to='generated_cover_letters/', blank=True)
    cover_letter_jpg = models.ImageField(upload_to='generated_cover_letters/', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CV Request for {self.job_title} at {self.company_name}"

# Pydantic models for validation
class TechnicalSkill(BaseModel):
    category: str = Field(..., min_length=1, max_length=30)
    skills: str = Field(..., min_length=1, max_length=150)

class Experience(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=50)
    company: str = Field(..., min_length=1, max_length=50)
    date_range: str = Field(..., min_length=1, max_length=30)
    responsibilities: List[str] = Field(..., min_items=1, max_items=3)

class Education(BaseModel):
    degree: str = Field(..., min_length=1, max_length=50)
    institution: str = Field(..., min_length=1, max_length=50)
    year: str = Field(..., min_length=4, max_length=4)
    achievements: Optional[List[str]] = Field(default=[], max_items=2)

class CV(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=50)
    job_title: str = Field(..., min_length=1, max_length=50)
    location: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., min_length=10, max_length=20)
    linkedin: str = Field(..., min_length=1, max_length=100)
    professional_summary: str = Field(..., min_length=50, max_length=300)
    technical_skills: List[TechnicalSkill] = Field(..., min_items=1, max_items=5)
    experience: List[Experience] = Field(..., min_items=1, max_items=3)
    education: List[Education] = Field(..., min_items=1, max_items=2)
    certifications: Optional[List[str]] = Field(default=[], max_items=5)

class CoverLetter(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=50)
    address: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=2, max_length=2)
    zip: str = Field(..., min_length=5, max_length=10)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str = Field(..., min_length=10, max_length=20)
    date: str = Field(...)
    hiring_manager_name: str = Field(..., min_length=1, max_length=50)
    job_title: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=50)
    company_address: str = Field(..., min_length=1, max_length=100)
    company_city: str = Field(..., min_length=1, max_length=50)
    company_state: str = Field(..., min_length=2, max_length=2)
    company_zip: str = Field(..., min_length=5, max_length=10)
    paragraphs: List[str] = Field(..., min_items=3, max_items=3)
    closing_paragraph: str = Field(..., min_length=20, max_length=300)
