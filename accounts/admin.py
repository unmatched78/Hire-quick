from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile, RecruiterProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'is_verified')}),
    )

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'current_title', 'location', 'experience_years')
    search_fields = ('first_name', 'last_name', 'user__email', 'current_title')
    list_filter = ('experience_years', 'location')

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'company', 'title', 'department')
    search_fields = ('first_name', 'last_name', 'user__email', 'title')
    list_filter = ('company', 'department')

admin.site.register(User, CustomUserAdmin)
