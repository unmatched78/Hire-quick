from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='detail'),
    path('create/', views.JobCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.JobUpdateView.as_view(), name='update'),
    path('<int:pk>/save/', views.save_job, name='save_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    
    # Dynamic application form management
    path('<int:pk>/setup-form/', views.setup_application_form, name='setup_application_form'),
    path('<int:pk>/add-field/', views.add_application_form_field, name='add_application_form_field'),
    path('<int:pk>/delete-field/<int:field_id>/', views.delete_application_form_field, name='delete_application_form_field'),
    path('<int:pk>/reorder-fields/', views.reorder_application_form_fields, name='reorder_application_form_fields'),
]
