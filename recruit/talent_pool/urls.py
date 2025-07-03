from django.urls import path
from . import views

app_name = 'talent_pool'

urlpatterns = [
    # Talent Pool Management
    path('', views.TalentPoolListView.as_view(), name='list'),
    path('create/', views.TalentPoolCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TalentPoolDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TalentPoolUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TalentPoolDeleteView.as_view(), name='delete'),
    
    # Candidate Management
    path('<int:pool_id>/add-candidate/', views.add_candidate_to_pool, name='add_candidate'),
    path('candidate/<int:candidate_id>/remove/<int:pool_id>/', views.remove_candidate_from_pool, name='remove_candidate'),
    path('candidate/<int:pk>/update/', views.update_pool_candidate, name='update_candidate'),
    
    # Job Matching
    path('matches/', views.candidate_job_matches, name='candidate_matches'),
    path('match/<int:pk>/', views.job_match_detail, name='job_match_detail'),
    path('match/<int:pk>/update-status/', views.update_match_status, name='update_match_status'),
    path('preferences/', views.update_candidate_preferences, name='update_preferences'),
    
    # Matching Operations
    path('generate-matches/', views.generate_job_matches, name='generate_matches'),
    path('bulk-add-candidates/', views.bulk_add_candidates, name='bulk_add_candidates'),
    
    # Analytics
    path('analytics/', views.matching_analytics, name='analytics'),
    path('pool/<int:pk>/analytics/', views.pool_analytics, name='pool_analytics'),
    
    # API endpoints
    path('api/search-candidates/', views.search_candidates_api, name='search_candidates_api'),
    path('api/match-preview/', views.match_preview_api, name='match_preview_api'),
]
