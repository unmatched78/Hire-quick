from django.contrib import admin
from .models import Job, SavedJob

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'recruiter', 'job_type', 'location', 'status', 'created_at')
    list_filter = ('job_type', 'status', 'remote_ok', 'created_at', 'company')
    search_fields = ('title', 'company__name', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'recruiter', 'description')
        }),
        ('Job Details', {
            'fields': ('job_type', 'location', 'remote_ok', 'requirements', 'preferred_skills')
        }),
        ('Compensation & Experience', {
            'fields': ('salary_min', 'salary_max', 'experience_min', 'experience_max', 'education_required')
        }),
        ('Additional Information', {
            'fields': ('benefits', 'status', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('candidate__first_name', 'candidate__last_name', 'job__title')
