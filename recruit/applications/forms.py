from django import forms
from .models import Application, Interview, ApplicationFile
from jobs.forms import DynamicApplicationForm

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write a compelling cover letter explaining why you are the perfect fit for this role...',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].widget.attrs['class'] = 'form-control'
        self.fields['cover_letter'].required = True

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Add internal notes about this application...',
                'class': 'form-control'
            }),
        }

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'interview_type', 'scheduled_at', 'duration_minutes', 
            'location', 'status'
        ]
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Meeting room, address, or video call link',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'scheduled_at':
                field.widget.attrs['class'] = 'form-control'

class InterviewFeedbackForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['feedback', 'rating', 'status']
        widgets = {
            'feedback': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Provide detailed feedback about the interview...',
                'class': 'form-control'
            }),
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
