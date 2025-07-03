from django import forms
from .models import JobGenerationRequest, InterviewSchedule, CalendarEvent
from jobs.models import Job

class JobGenerationForm(forms.ModelForm):
    class Meta:
        model = JobGenerationRequest
        fields = [
            'job_title', 'company_description', 'requirements_input', 
            'industry', 'experience_level', 'employment_type', 'remote_option'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of your company...'}),
            'requirements_input': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what you\'re looking for in a candidate...'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technology, Healthcare, Finance'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'remote_option': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requirements_input'].help_text = 'Describe the key skills, experience, and qualifications you\'re looking for'

class JobCreationFromAIForm(forms.ModelForm):
    """Form to create a job from AI-generated content"""
    use_ai_description = forms.BooleanField(required=False, initial=True, label="Use AI-generated description")
    use_ai_requirements = forms.BooleanField(required=False, initial=True, label="Use AI-generated requirements")
    use_ai_benefits = forms.BooleanField(required=False, initial=True, label="Use AI-generated benefits")
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'location', 'job_type', 'remote_ok',
            'salary_min', 'salary_max', 'experience_min', 'experience_max',
            'education_required', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'experience_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'experience_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'education_required': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = InterviewSchedule
        fields = [
            'interview_type', 'scheduled_date', 'scheduled_time', 'duration_minutes',
            'location', 'meeting_link', 'meeting_id', 'agenda', 'preparation_notes'
        ]
        widgets = {
            'interview_type': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 480}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meeting room or address'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/j/...'}),
            'meeting_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meeting ID/Password'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Interview agenda and topics to cover...'}),
            'preparation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes for the candidate to prepare...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duration_minutes'].initial = 60

class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'event_type', 'start_date', 'start_time',
            'end_date', 'end_time', 'email_reminder', 'reminder_minutes_before'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reminder_minutes_before': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 1440}),
        }

class InterviewFeedbackForm(forms.ModelForm):
    class Meta:
        model = InterviewSchedule
        fields = ['feedback', 'rating', 'recommendation', 'status']
        widgets = {
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-control'}),
            'recommendation': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
