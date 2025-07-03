from django.urls import path
from . import views
from .resume_parsing_views import (
    parse_resume, view_parsed_resume, ParsedResumeListView, 
    bulk_parse_resumes, resume_analytics
)

app_name = 'applications'

urlpatterns = [
    # Application management
    path('apply/<int:job_id>/', views.apply_for_job, name='apply'),
    path('my-applications/', views.MyApplicationsView, name='my_applications'),
    path('recruiter-applications/', views.RecruiterApplicationsView, name='recruiter_applications'),
    path('<int:pk>/', views.ApplicationDetailView, name='detail'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_status'),
    path('<int:pk>/add-notes/', views.add_application_notes, name='add_notes'),
    
    # Interview management
    path('<int:pk>/schedule-interview/', views.schedule_interview, name='schedule_interview'),
    path('interview/<int:pk>/', views.interview_detail, name='interview_detail'),
    
    # File management
    path('file/<int:file_id>/download/', views.download_file, name='download_file'),
    
    # Resume parsing
    path('<int:application_id>/parse-resume/', parse_resume, name='parse_resume'),
    path('<int:application_id>/parsed-resume/', view_parsed_resume, name='view_parsed_resume'),
    path('parsed-resumes/', ParsedResumeListView.as_view(), name='parsed_resume_list'),
    path('bulk-parse-resumes/', bulk_parse_resumes, name='bulk_parse_resumes'),
    path('resume-analytics/', resume_analytics, name='resume_analytics'),
]
