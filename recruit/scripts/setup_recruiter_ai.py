#!/usr/bin/env python
"""
Setup script for Recruiter AI features
Run this after installing the new requirements
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Setup recruiter AI features"""
    print("Setting up Recruiter AI features...")
    
    # Create migrations
    print("Creating migrations...")
    execute_from_command_line(['manage.py', 'makemigrations', 'recruiter_ai'])
    
    # Apply migrations
    print("Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Recruiter AI setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure OPENAI_API_KEY is set in your environment variables")
    print("2. Configure email settings for interview notifications")
    print("3. Set up Redis for Celery (for background tasks)")
    print("4. Test the AI features in the recruiter dashboard")

if __name__ == '__main__':
    main()
