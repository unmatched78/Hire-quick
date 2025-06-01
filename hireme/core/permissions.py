from rest_framework.permissions import BasePermission
from .models import User

class IsCompanyRep(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'company_rep'

class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'job_seeker'