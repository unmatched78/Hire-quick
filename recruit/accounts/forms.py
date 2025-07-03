from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from allauth.account.forms import SignupForm
from .models import User, CandidateProfile, RecruiterProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomSignupForm(SignupForm):
    """Custom signup form with user type selection"""
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, request):
        user = super().save(request)
        user.user_type = self.cleaned_data['user_type']
        user.save()
        return user

class CandidateProfileForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter skills separated by commas'}),
        help_text='Enter your skills separated by commas (e.g., Python, Django, JavaScript)',
        required=False
    )
    
    class Meta:
        model = CandidateProfile
        fields = [
            'first_name', 'last_name', 'location', 'linkedin_url', 'github_url',
            'portfolio_url', 'resume', 'summary', 'skills', 'experience_years',
            'current_title', 'salary_expectation', 'availability', 'profile_picture'
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
            'salary_expectation': forms.NumberInput(attrs={'placeholder': 'Expected salary in USD'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['resume', 'profile_picture']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control-file'
        
        # Pre-populate skills field if it's a list
        if self.instance and self.instance.skills:
            if isinstance(self.instance.skills, list):
                self.fields['skills'].initial = ', '.join(self.instance.skills)
    
    def clean_skills(self):
        skills_str = self.cleaned_data.get('skills', '')
        if skills_str:
            # Convert comma-separated string to list
            skills_list = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
            return skills_list
        return []

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = [
            'first_name', 'last_name', 'company', 'title', 'department', 'profile_picture'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'profile_picture':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control-file'
