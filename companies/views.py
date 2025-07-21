from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Company

class CompanyListView(ListView):
    model = Company
    template_name = 'companies/list.html'
    context_object_name = 'companies'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Company.objects.all().order_by('name')
        search = self.request.GET.get('search')
        industry = self.request.GET.get('industry')
        size = self.request.GET.get('size')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        if industry:
            queryset = queryset.filter(industry__icontains=industry)
        if size:
            queryset = queryset.filter(size=size)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['industries'] = Company.objects.values_list('industry', flat=True).distinct()
        context['sizes'] = Company.COMPANY_SIZE_CHOICES
        return context

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'companies/detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_jobs'] = self.object.jobs.filter(status='active')[:5]
        return context
