from django import forms
from django.forms import formset_factory
from .models import Job, ApplicationFormField

class JobForm(forms.ModelForm):
    requirements = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter requirements separated by commas'}),
        help_text='Enter job requirements separated by commas',
        required=False
    )
    
    preferred_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter preferred skills separated by commas'}),
        help_text='Enter preferred skills separated by commas',
        required=False
    )
    
    benefits = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter benefits separated by commas'}),
        help_text='Enter benefits separated by commas',
        required=False
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'preferred_skills', 'location',
            'job_type', 'remote_ok', 'salary_min', 'salary_max', 'experience_min',
            'experience_max', 'education_required', 'benefits', 'status', 'expires_at',
            'has_custom_application_form'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'has_custom_application_form': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'customApplicationFormToggle'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'has_custom_application_form':
                field.widget.attrs['class'] = 'form-control'
    
    def clean_requirements(self):
        requirements_str = self.cleaned_data.get('requirements', '')
        if requirements_str:
            return [req.strip() for req in requirements_str.split(',') if req.strip()]
        return []
    
    def clean_preferred_skills(self):
        skills_str = self.cleaned_data.get('preferred_skills', '')
        if skills_str:
            return [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        return []
    
    def clean_benefits(self):
        benefits_str = self.cleaned_data.get('benefits', '')
        if benefits_str:
            return [benefit.strip() for benefit in benefits_str.split(',') if benefit.strip()]
        return []

class ApplicationFormFieldForm(forms.ModelForm):
    choices_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter options separated by new lines (for dropdown/radio/checkbox fields)'
        }),
        help_text='Enter each option on a new line'
    )
    
    allowed_file_types_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'pdf, doc, docx, jpg, png'
        }),
        help_text='Enter allowed file extensions separated by commas'
    )
    
    class Meta:
        model = ApplicationFormField
        fields = [
            'field_type', 'label', 'help_text', 'placeholder', 'is_required',
            'max_file_size_mb', 'max_duration_minutes', 'min_rating', 'max_rating'
        ]
        widgets = {
            'field_type': forms.Select(attrs={'class': 'form-control field-type-select'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter field label/question'}),
            'help_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'placeholder': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_file_size_mb': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'max_duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 60}),
            'min_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'max_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate choices and file types if editing
        if self.instance and self.instance.pk:
            if self.instance.choices:
                self.fields['choices_text'].initial = '\n'.join(self.instance.choices)
            if self.instance.allowed_file_types:
                self.fields['allowed_file_types_text'].initial = ', '.join(self.instance.allowed_file_types)
    
    def clean_choices_text(self):
        choices_text = self.cleaned_data.get('choices_text', '')
        if choices_text:
            return [choice.strip() for choice in choices_text.split('\n') if choice.strip()]
        return []
    
    def clean_allowed_file_types_text(self):
        file_types_text = self.cleaned_data.get('allowed_file_types_text', '')
        if file_types_text:
            return [ft.strip().lower() for ft in file_types_text.split(',') if ft.strip()]
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save choices
        choices = self.cleaned_data.get('choices_text', [])
        if choices:
            instance.choices = choices
        
        # Save allowed file types
        file_types = self.cleaned_data.get('allowed_file_types_text', [])
        if file_types:
            instance.allowed_file_types = file_types
        
        if commit:
            instance.save()
        return instance

# Formset for managing multiple application form fields
ApplicationFormFieldFormSet = formset_factory(
    ApplicationFormFieldForm,
    extra=1,
    can_delete=True
)

class JobSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Job title, keywords, or company',
            'class': 'form-control'
        })
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Location',
            'class': 'form-control'
        })
    )
    
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    remote_ok = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    salary_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Minimum salary',
            'class': 'form-control'
        })
    )

class DynamicApplicationForm(forms.Form):
    """Dynamically generated form based on job's custom fields"""
    
    def __init__(self, job, *args, **kwargs):
        self.job = job
        super().__init__(*args, **kwargs)
        
        # Add custom fields based on job requirements
        for field in job.application_form_fields.all().order_by('order'):
            self.add_custom_field(field)
    
    def add_custom_field(self, form_field):
        """Add a custom field to the form"""
        field_name = f'field_{form_field.id}'
        
        # Get base field attributes
        attrs = form_field.get_field_widget_attrs()
        
        if form_field.field_type == 'text':
            field = forms.CharField(
                max_length=500,
                widget=forms.TextInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'textarea':
            field = forms.CharField(
                widget=forms.Textarea(attrs=attrs)
            )
        
        elif form_field.field_type == 'email':
            field = forms.EmailField(
                widget=forms.EmailInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'phone':
            field = forms.CharField(
                max_length=20,
                widget=forms.TextInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'number':
            field = forms.IntegerField(
                widget=forms.NumberInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'date':
            field = forms.DateField(
                widget=forms.DateInput(attrs={**attrs, 'type': 'date'})
            )
        
        elif form_field.field_type in ['file', 'resume', 'portfolio']:
            field = forms.FileField(
                widget=forms.FileInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'video':
            field = forms.FileField(
                widget=forms.FileInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'audio':
            field = forms.FileField(
                widget=forms.FileInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'url':
            field = forms.URLField(
                widget=forms.URLInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'select':
            choices = [('', '-- Select an option --')] + [(choice, choice) for choice in form_field.choices]
            field = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs=attrs)
            )
        
        elif form_field.field_type == 'radio':
            choices = [(choice, choice) for choice in form_field.choices]
            field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
            )
        
        elif form_field.field_type == 'checkbox':
            choices = [(choice, choice) for choice in form_field.choices]
            field = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
            )
        
        elif form_field.field_type == 'boolean':
            field = forms.BooleanField(
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
        
        elif form_field.field_type == 'rating':
            choices = [(i, f'{i}') for i in range(form_field.min_rating, form_field.max_rating + 1)]
            field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input rating-field'})
            )
        
        elif form_field.field_type in ['linkedin', 'github']:
            field = forms.URLField(
                widget=forms.URLInput(attrs=attrs)
            )
        
        elif form_field.field_type == 'cover_letter':
            field = forms.CharField(
                widget=forms.Textarea(attrs={**attrs, 'rows': 6})
            )
        
        else:
            # Default to text field
            field = forms.CharField(
                widget=forms.TextInput(attrs=attrs)
            )
        
        # Set field properties
        field.label = form_field.label
        field.help_text = form_field.help_text
        field.required = form_field.is_required
        
        # Add the field to the form
        self.fields[field_name] = field
    
    def get_form_responses(self):
        """Get cleaned form responses mapped to field IDs"""
        responses = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('field_'):
                field_id = field_name.replace('field_', '')
                responses[field_id] = value
        return responses
