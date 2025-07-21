from django.urls import path
from . import views

app_name = 'background_verification'

urlpatterns = [
    # Dashboard and main views
    path('', views.verification_dashboard, name='dashboard'),
    path('requests/', views.BackgroundCheckListView.as_view(), name='request_list'),
    path('reports/', views.verification_reports, name='reports'),
    
    # Background check management
    path('create/<int:application_id>/', views.create_background_check, name='create_request'),
    path('request/<uuid:request_id>/', views.request_detail, name='request_detail'),
    
    # Candidate portal
    path('portal/<uuid:request_id>/', views.candidate_portal, name='candidate_portal'),
    path('consent/<uuid:request_id>/', views.give_consent, name='give_consent'),
    path('upload/<uuid:request_id>/', views.upload_document, name='upload_document'),
    
    # Document management
    path('document/<int:document_id>/review/', views.review_document, name='review_document'),
    path('request/<uuid:request_id>/request-documents/', views.send_document_request, name='send_document_request'),
    
    # Bulk actions
    path('bulk-action/', views.bulk_action, name='bulk_action'),
]
