from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, CandidateProfile, RecruiterProfile
from .forms import CandidateProfileForm, RecruiterProfileForm

@login_required
def profile_setup(request):
    """Setup profile after registration"""
    user = request.user
    
    if user.user_type == 'candidate':
        profile = getattr(user, 'candidate_profile', None)
        if not profile:
            profile = CandidateProfile.objects.create(user=user)
            
        if request.method == 'POST':
            form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save()
                profile.profile_completed = True
                profile.save()
                messages.success(request, 'Profile completed successfully!')
                return redirect('dashboard:home')
        else:
            form = CandidateProfileForm(instance=profile)
        
        return render(request, 'accounts/candidate_profile_setup.html', {
            'form': form,
            'profile_completion': profile.calculate_profile_completion()
        })
    
    elif user.user_type == 'recruiter':
        profile = getattr(user, 'recruiter_profile', None)
        if not profile:
            profile = RecruiterProfile.objects.create(user=user)
            
        if request.method == 'POST':
            form = RecruiterProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save()
                profile.profile_completed = True
                profile.save()
                messages.success(request, 'Profile completed successfully!')
                return redirect('dashboard:home')
        else:
            form = RecruiterProfileForm(instance=profile)
        
        return render(request, 'accounts/recruiter_profile_setup.html', {'form': form})
    
    return redirect('dashboard:home')

class CandidateProfileView(LoginRequiredMixin, DetailView):
    model = CandidateProfile
    template_name = 'accounts/candidate_profile.html'
    context_object_name = 'profile'

class RecruiterProfileView(LoginRequiredMixin, DetailView):
    model = RecruiterProfile
    template_name = 'accounts/recruiter_profile.html'
    context_object_name = 'profile'

@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    
    if user.user_type == 'candidate':
        profile = getattr(user, 'candidate_profile', None)
        if not profile:
            profile = CandidateProfile.objects.create(user=user)
            
        if request.method == 'POST':
            form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = CandidateProfileForm(instance=profile)
        
        return render(request, 'accounts/edit_candidate_profile.html', {
            'form': form,
            'profile_completion': profile.calculate_profile_completion()
        })
    
    elif user.user_type == 'recruiter':
        profile = getattr(user, 'recruiter_profile', None)
        if not profile:
            profile = RecruiterProfile.objects.create(user=user)
            
        if request.method == 'POST':
            form = RecruiterProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = RecruiterProfileForm(instance=profile)
        
        return render(request, 'accounts/edit_recruiter_profile.html', {'form': form})
    
    return redirect('dashboard:home')

@login_required
def my_profile(request):
    """View current user's profile"""
    user = request.user
    
    if user.user_type == 'candidate':
        profile = getattr(user, 'candidate_profile', None)
        if not profile:
            profile = CandidateProfile.objects.create(user=user)
        return render(request, 'accounts/my_candidate_profile.html', {
            'profile': profile,
            'profile_completion': profile.calculate_profile_completion()
        })
    
    elif user.user_type == 'recruiter':
        profile = getattr(user, 'recruiter_profile', None)
        if not profile:
            profile = RecruiterProfile.objects.create(user=user)
        return render(request, 'accounts/my_recruiter_profile.html', {'profile': profile})
    
    return redirect('dashboard:home')
