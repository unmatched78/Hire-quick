from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'size', 'location', 'created_at')
    search_fields = ('name', 'industry', 'location')
    list_filter = ('industry', 'size', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
