from django.urls import path
from . import views

app_name = 'recruiter_ai'

urlpatterns = [
    # AI Tools
    path('', views.ai_tools_home, name='home'),
    path('generate-job/', views.generate_job_description, name='generate_job'),
    path('generation/<int:pk>/', views.generation_detail, name='generation_detail'),
    path('create-job/<int:pk>/', views.create_job_from_ai, name='create_job_from_ai'),
    
    # Calendar and Interviews
    path('calendar/', views.calendar_view, name='calendar'),
    path('schedule-interview/<int:application_id>/', views.schedule_interview, name='schedule_interview'),
    path('interview/<int:pk>/', views.interview_detail, name='interview_detail'),
    path('interview/<int:pk>/feedback/', views.interview_feedback, name='interview_feedback'),
    
    # AJAX endpoints
    path('api/interview-suggestions/', views.get_interview_suggestions, name='interview_suggestions'),
]
