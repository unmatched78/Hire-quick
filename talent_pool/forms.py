from django import forms
from django.core.exceptions import ValidationError
from .models import TalentPool, TalentPoolCandidate, CandidatePreferences
from jobs.models import Job

class TalentPoolForm(forms.ModelForm):
    required_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter skills separated by commas'}),
        required=False,
        help_text='Enter required skills separated by commas'
    )
    preferred_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter preferred skills separated by commas'}),
        required=False,
        help_text='Enter preferred skills separated by commas'
    )
    locations = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter locations separated by commas'}),
        required=False,
        help_text='Enter preferred locations separated by commas'
    )
    education_requirements = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter education requirements separated by commas'}),
        required=False,
        help_text='Enter education requirements separated by commas'
    )
    
    class Meta:
        model = TalentPool
        fields = [
            'name', 'description', 'pool_type', 'status',
            'required_skills', 'preferred_skills', 'min_experience', 'max_experience',
            'locations', 'education_requirements'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'pool_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'min_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'max_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_exp = cleaned_data.get('min_experience')
        max_exp = cleaned_data.get('max_experience')
        
        if min_exp and max_exp and min_exp > max_exp:
            raise ValidationError('Minimum experience cannot be greater than maximum experience.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert comma-separated strings to lists
        if self.cleaned_data.get('required_skills'):
            instance.required_skills = [
                skill.strip() for skill in self.cleaned_data['required_skills'].split(',')
                if skill.strip()
            ]
        
        if self.cleaned_data.get('preferred_skills'):
            instance.preferred_skills = [
                skill.strip() for skill in self.cleaned_data['preferred_skills'].split(',')
                if skill.strip()
            ]
        
        if self.cleaned_data.get('locations'):
            instance.locations = [
                loc.strip() for loc in self.cleaned_data['locations'].split(',')
                if loc.strip()
            ]
        
        if self.cleaned_data.get('education_requirements'):
            instance.education_requirements = [
                req.strip() for req in self.cleaned_data['education_requirements'].split(',')
                if req.strip()
            ]
        
        if commit:
            instance.save()
        return instance

class TalentPoolCandidateForm(forms.ModelForm):
    class Meta:
        model = TalentPoolCandidate
        fields = ['status', 'priority', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class CandidatePreferencesForm(forms.ModelForm):
    job_types = forms.MultipleChoiceField(
        choices=CandidatePreferences.JOB_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    preferred_roles = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter preferred job titles separated by commas'}),
        required=False,
        help_text='Enter preferred job titles separated by commas'
    )
    industries = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter preferred industries separated by commas'}),
        required=False,
        help_text='Enter preferred industries separated by commas'
    )
    company_sizes = forms.MultipleChoiceField(
        choices=[
            ('startup', 'Startup (1-50)'),
            ('small', 'Small (51-200)'),
            ('medium', 'Medium (201-1000)'),
            ('large', 'Large (1000+)'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    preferred_locations = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter preferred locations separated by commas'}),
        required=False,
        help_text='Enter preferred locations separated by commas'
    )
    
    class Meta:
        model = CandidatePreferences
        fields = [
            'job_types', 'preferred_roles', 'industries', 'company_sizes',
            'preferred_locations', 'remote_preference', 'willing_to_relocate',
            'min_salary', 'max_salary', 'salary_negotiable',
            'available_from', 'notice_period_weeks',
            'email_notifications', 'match_frequency'
        ]
        widgets = {
            'remote_preference': forms.Select(attrs={'class': 'form-select'}),
            'willing_to_relocate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'max_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'salary_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notice_period_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'match_frequency': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get('min_salary')
        max_salary = cleaned_data.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Convert comma-separated strings to lists
        if self.cleaned_data.get('preferred_roles'):
            instance.preferred_roles = [
                role.strip() for role in self.cleaned_data['preferred_roles'].split(',')
                if role.strip()
            ]
        
        if self.cleaned_data.get('industries'):
            instance.industries = [
                industry.strip() for industry in self.cleaned_data['industries'].split(',')
                if industry.strip()
            ]
        
        if self.cleaned_data.get('preferred_locations'):
            instance.preferred_locations = [
                loc.strip() for loc in self.cleaned_data['preferred_locations'].split(',')
                if loc.strip()
            ]
        
        if commit:
            instance.save()
        return instance

class JobMatchFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] ,#+ list(CandidatePreferences.STATUS_CHOICES)
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_score = forms.IntegerField(
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min match score'})
    )
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
