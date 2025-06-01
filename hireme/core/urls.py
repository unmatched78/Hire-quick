from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, JobSeekerViewSet, CompanyViewSet, JobViewSet, ApplicationViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'jobseekers', JobSeekerViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]