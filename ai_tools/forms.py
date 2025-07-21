from django import forms
from .models import CVGenerationRequest

class CVGenerationForm(forms.ModelForm):
    class Meta:
        model = CVGenerationRequest
        fields = ['job_url']
        widgets = {
            'job_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/job-posting',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_url'].help_text = 'Enter the URL of the job posting you want to apply for'

class BaseProfileForm(forms.Form):
    """Base form for user profile information"""
    full_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    current_title = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    linkedin = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    professional_summary = forms.CharField(
        max_length=300,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Enter your skills separated by commas'
    )
    experience = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        help_text='Describe your work experience'
    )
    education = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='List your educational background'
    )
    certifications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        help_text='List any relevant certifications (optional)'
    )
