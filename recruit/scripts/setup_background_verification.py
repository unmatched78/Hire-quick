#!/usr/bin/env python
"""
Setup script for Background Verification system
Run this script to initialize the background verification system with default data
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
django.setup()

from background_verification.models import (
    VerificationProvider, BackgroundCheckPackage, VerificationTemplate
)

def create_verification_providers():
    """Create default verification providers"""
    providers_data = [
        {
            'name': 'AI Criminal Check',
            'provider_type': 'criminal',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS'],
            'average_turnaround_hours': 24,
            'cost_per_check': 25.00,
        },
        {
            'name': 'AI Employment Verifier',
            'provider_type': 'employment',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA'],
            'average_turnaround_hours': 48,
            'cost_per_check': 15.00,
        },
        {
            'name': 'AI Education Verifier',
            'provider_type': 'education',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA', 'IND'],
            'average_turnaround_hours': 72,
            'cost_per_check': 20.00,
        },
        {
            'name': 'AI Identity Verifier',
            'provider_type': 'identity',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA', 'IND', 'BRA'],
            'average_turnaround_hours': 12,
            'cost_per_check': 10.00,
        },
        {
            'name': 'AI Credit Check',
            'provider_type': 'credit',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS'],
            'average_turnaround_hours': 24,
            'cost_per_check': 30.00,
        },
        {
            'name': 'AI Driving Record',
            'provider_type': 'driving',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS'],
            'average_turnaround_hours': 24,
            'cost_per_check': 20.00,
        },
        {
            'name': 'AI Reference Check',
            'provider_type': 'reference',
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA', 'IND'],
            'average_turnaround_hours': 48,
            'cost_per_check': 25.00,
        },
        {
            'name': 'AI International Background',
            'provider_type': 'international',
            'supported_countries': ['ALL'],
            'average_turnaround_hours': 120,
            'cost_per_check': 75.00,
        },
    ]
    
    for provider_data in providers_data:
        provider, created = VerificationProvider.objects.get_or_create(
            name=provider_data['name'],
            provider_type=provider_data['provider_type'],
            defaults=provider_data
        )
        if created:
            print(f"Created provider: {provider.name}")
        else:
            print(f"Provider already exists: {provider.name}")

def create_background_check_packages():
    """Create default background check packages"""
    packages_data = [
        {
            'name': 'Basic Package',
            'package_type': 'basic',
            'description': 'Essential background checks for most positions',
            'included_checks': ['criminal', 'identity'],
            'estimated_cost': 35.00,
            'estimated_turnaround_days': 2,
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS'],
        },
        {
            'name': 'Standard Package',
            'package_type': 'standard',
            'description': 'Comprehensive checks for professional positions',
            'included_checks': ['criminal', 'identity', 'employment', 'education'],
            'estimated_cost': 75.00,
            'estimated_turnaround_days': 3,
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA'],
        },
        {
            'name': 'Comprehensive Package',
            'package_type': 'comprehensive',
            'description': 'Thorough verification for sensitive positions',
            'included_checks': ['criminal', 'identity', 'employment', 'education', 'reference', 'credit'],
            'estimated_cost': 130.00,
            'estimated_turnaround_days': 5,
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA'],
        },
        {
            'name': 'Executive Package',
            'package_type': 'executive',
            'description': 'Premium verification for executive and leadership roles',
            'included_checks': ['criminal', 'identity', 'employment', 'education', 'reference', 'credit', 'social_media'],
            'estimated_cost': 200.00,
            'estimated_turnaround_days': 7,
            'supported_countries': ['USA', 'CAN', 'GBR', 'AUS', 'DEU', 'FRA', 'IND'],
        },
        {
            'name': 'International Package',
            'package_type': 'custom',
            'description': 'Global verification for international candidates',
            'included_checks': ['criminal', 'identity', 'employment', 'education', 'international'],
            'estimated_cost': 150.00,
            'estimated_turnaround_days': 10,
            'supported_countries': ['ALL'],
        },
    ]
    
    for package_data in packages_data:
        package, created = BackgroundCheckPackage.objects.get_or_create(
            name=package_data['name'],
            package_type=package_data['package_type'],
            defaults=package_data
        )
        if created:
            print(f"Created package: {package.name}")
        else:
            print(f"Package already exists: {package.name}")

def create_email_templates():
    """Create default email templates"""
    templates_data = [
        {
            'name': 'Default Consent Request',
            'template_type': 'consent_request',
            'subject': 'Background Check Consent Required - {{job_title}} at {{company_name}}',
            'body': '''Dear {{candidate_name}},

{{company_name}} has requested a background check as part of your application for the {{job_title}} position.

Please click the link below to review the details and provide your consent:
{{portal_link}}

This background check is an important step in our hiring process and helps us ensure a safe and secure workplace for all employees.

If you have any questions, please contact us at {{contact_email}}

Best regards,
{{company_name}} Hiring Team''',
            'includes_legal_disclosure': True,
            'is_default': True,
        },
        {
            'name': 'Document Request',
            'template_type': 'document_request',
            'subject': 'Additional Documents Required - Background Check',
            'body': '''Dear {{candidate_name}},

We need additional documents to complete your background check for the {{job_title}} position at {{company_name}}.

Please upload the requested documents using the following link:
{{portal_link}}

Required documents:
- Government-issued photo ID
- Proof of address
- Educational certificates (if applicable)
- Employment verification letters (if applicable)

Please submit these documents within 5 business days to avoid delays in processing your application.

If you have any questions, please contact us at {{contact_email}}

Best regards,
{{company_name}} Hiring Team''',
            'is_default': True,
        },
        {
            'name': 'Status Update',
            'template_type': 'status_update',
            'subject': 'Background Check Status Update - {{job_title}}',
            'body': '''Dear {{candidate_name}},

We wanted to update you on the status of your background check for the {{job_title}} position at {{company_name}}.

Current Status: In Progress
Expected Completion: {{due_date}}

You can check the current status anytime by visiting:
{{portal_link}}

We appreciate your patience as we complete this important step in our hiring process.

If you have any questions, please contact us at {{contact_email}}

Best regards,
{{company_name}} Hiring Team''',
            'is_default': True,
        },
        {
            'name': 'Completion Notice',
            'template_type': 'completion_notice',
            'subject': 'Background Check Complete - {{job_title}}',
            'body': '''Dear {{candidate_name}},

Your background check for the {{job_title}} position at {{company_name}} has been completed.

The results have been forwarded to our hiring team, and they will be in touch with you regarding the next steps in the hiring process.

Thank you for your cooperation throughout this process.

If you have any questions, please contact us at {{contact_email}}

Best regards,
{{company_name}} Hiring Team''',
            'is_default': True,
        },
        {
            'name': 'Reminder Notice',
            'template_type': 'reminder',
            'subject': 'Reminder: Background Check Action Required',
            'body': '''Dear {{candidate_name}},

This is a friendly reminder that we are still waiting for your action on the background check for the {{job_title}} position at {{company_name}}.

Please visit the following link to complete the required steps:
{{portal_link}}

To avoid delays in your application process, please complete this within the next 2 business days.

If you have any questions or need assistance, please contact us at {{contact_email}}

Best regards,
{{company_name}} Hiring Team''',
            'is_default': True,
        },
    ]
    
    for template_data in templates_data:
        template, created = VerificationTemplate.objects.get_or_create(
            name=template_data['name'],
            template_type=template_data['template_type'],
            defaults=template_data
        )
        if created:
            print(f"Created template: {template.name}")
        else:
            print(f"Template already exists: {template.name}")

def main():
    """Main setup function"""
    print("Setting up Background Verification system...")
    print("=" * 50)
    
    print("\n1. Creating verification providers...")
    create_verification_providers()
    
    print("\n2. Creating background check packages...")
    create_background_check_packages()
    
    print("\n3. Creating email templates...")
    create_email_templates()
    
    print("\n" + "=" * 50)
    print("Background Verification system setup complete!")
    print("\nNext steps:")
    print("1. Configure your OPENAI_API_KEY in environment variables")
    print("2. Set up email configuration for notifications")
    print("3. Configure Celery for background task processing")
    print("4. Test the system with a sample background check request")
    print("\nThe system is now ready to use!")

if __name__ == '__main__':
    main()
