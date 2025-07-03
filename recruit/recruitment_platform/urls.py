from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    path('profile/', include('accounts.urls')),
    
    # Core functionality
    path('jobs/', include('jobs.urls')),
    path('applications/', include('applications.urls')),
    path('companies/', include('companies.urls')),
    path('dashboard/', include('dashboard.urls')),
    
    # AI Tools
    path('ai-tools/', include('ai_tools.urls')),
    path('recruiter-ai/', include('recruiter_ai.urls')),
    
    # Talent Pool and Matching
    path('talent-pool/', include('talent_pool.urls')),
    
    # Background Verification
    path('verification/', include('background_verification.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
