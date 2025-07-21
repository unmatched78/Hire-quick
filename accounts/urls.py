from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Profile management URLs
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.my_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('candidate/<int:pk>/', views.CandidateProfileView.as_view(), name='candidate_profile'),
    path('recruiter/<int:pk>/', views.RecruiterProfileView.as_view(), name='recruiter_profile'),
]
