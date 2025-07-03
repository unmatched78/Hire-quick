from django.urls import path
from . import views

app_name = 'ai_tools'

urlpatterns = [
    path('', views.ai_tools_home, name='home'),
    path('generate/', views.generate_cv_cover_letter, name='generate'),
    path('requests/', views.CVRequestListView.as_view(), name='request_list'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('download/<int:pk>/<str:file_type>/', views.download_file, name='download_file'),
]
