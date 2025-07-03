import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import date
from django.conf import settings
from .models import CV, CoverLetter, CVGenerationRequest
import tempfile

class JobApplicationCrew:
    """Simplified version of the AI crew for Django integration"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
    
    def extract_job_info(self, job_url):
        """Extract job information from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(job_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic job information
            title = self._extract_text(soup, ['h1', '.job-title', '.position-title'])
            company = self._extract_text(soup, ['.company-name', '.employer'])
            location = self._extract_text(soup, ['.location', '.job-location'])
            description = self._extract_text(soup, ['.job-description', '.description'])
            
            return {
                'title': title or 'Position Title',
                'company': company or 'Company Name',
                'location': location or 'Location',
                'description': description or 'Job Description'
            }
        
        except Exception as e:
            return {
                'title': 'Position Title',
                'company': 'Company Name',
                'location': 'Location',
                'description': 'Job Description',
                'error': str(e)
            }
    
    def _extract_text(self, soup, selectors):
        """Helper method to extract text using multiple selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ''
    
    def generate_cv_data(self, user_profile, job_info):
        """Generate CV data based on user profile and job info"""
        # This is a simplified version - in production, you'd use the actual AI
        skills_list = user_profile.get('skills', '').split(',')
        skills_categories = []
        
        if skills_list:
            # Group skills into categories (simplified)
            technical_skills = [skill.strip() for skill in skills_list if skill.strip()]
            if technical_skills:
                skills_categories.append({
                    'category': 'Technical Skills',
                    'skills': ', '.join(technical_skills[:10])  # Limit to 10 skills
                })
        
        cv_data = {
            'full_name': user_profile.get('full_name', 'Your Name'),
            'job_title': user_profile.get('current_title', 'Professional'),
            'location': user_profile.get('location', 'Your Location'),
            'email': user_profile.get('email', 'your.email@example.com'),
            'phone': user_profile.get('phone', '(555) 123-4567'),
            'linkedin': user_profile.get('linkedin', 'linkedin.com/in/yourprofile'),
            'professional_summary': user_profile.get('professional_summary', 'Professional summary goes here.'),
            'technical_skills': skills_categories or [{'category': 'Skills', 'skills': 'Add your skills here'}],
            'experience': [{
                'job_title': user_profile.get('current_title', 'Your Job Title'),
                'company': 'Your Company',
                'date_range': '2020 - Present',
                'responsibilities': [
                    'Key responsibility or achievement',
                    'Another important contribution',
                    'Third major accomplishment'
                ]
            }],
            'education': [{
                'degree': 'Your Degree',
                'institution': 'Your University',
                'year': '2020',
                'achievements': ['Academic achievement', 'Another accomplishment']
            }],
            'certifications': ['Relevant Certification 1', 'Relevant Certification 2']
        }
        
        return cv_data
    
    def generate_cover_letter_data(self, user_profile, job_info):
        """Generate cover letter data"""
        cover_letter_data = {
            'full_name': user_profile.get('full_name', 'Your Name'),
            'address': '123 Your Street',
            'city': user_profile.get('location', 'Your City').split(',')[0],
            'state': 'ST',
            'zip': '12345',
            'email': user_profile.get('email', 'your.email@example.com'),
            'phone': user_profile.get('phone', '(555) 123-4567'),
            'date': date.today().strftime('%B %d, %Y'),
            'hiring_manager_name': 'Hiring Manager',
            'job_title': job_info.get('title', 'Position'),
            'company_name': job_info.get('company', 'Company'),
            'company_address': '456 Company Street',
            'company_city': job_info.get('location', 'Company City').split(',')[0],
            'company_state': 'ST',
            'company_zip': '67890',
            'paragraphs': [
                f"I am writing to express my strong interest in the {job_info.get('title', 'position')} role at {job_info.get('company', 'your company')}. With my background in {user_profile.get('current_title', 'my field')}, I am excited about the opportunity to contribute to your team.",
                f"In my current role, I have developed expertise in {user_profile.get('skills', 'relevant skills').split(',')[0] if user_profile.get('skills') else 'key areas'}. My experience aligns well with the requirements outlined in your job posting, particularly in areas that would benefit your organization.",
                "I am particularly drawn to this opportunity because it represents a chance to apply my skills in a new context while contributing to meaningful work. I would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team's success."
            ],
            'closing_paragraph': "Thank you for considering my application. I look forward to hearing from you and discussing how I can contribute to your organization."
        }
        
        return cover_letter_data
    
    def process_job_application(self, job_url, user_profile, request_id):
        """Main method to process job application"""
        try:
            # Extract job information
            job_info = self.extract_job_info(job_url)
            
            # Update the request with job info
            cv_request = CVGenerationRequest.objects.get(id=request_id)
            cv_request.job_title = job_info['title']
            cv_request.company_name = job_info['company']
            cv_request.save()
            
            # Generate CV and Cover Letter data
            cv_data = self.generate_cv_data(user_profile, job_info)
            cover_letter_data = self.generate_cover_letter_data(user_profile, job_info)
            
            # In a real implementation, you would:
            # 1. Validate data with Pydantic models
            # 2. Render HTML templates
            # 3. Convert to PDF and JPEG
            # 4. Save files to the model
            
            # For now, we'll create placeholder files
            self._create_placeholder_files(cv_request, cv_data, cover_letter_data)
            
            return {
                'success': True,
                'cv_data': cv_data,
                'cover_letter_data': cover_letter_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_placeholder_files(self, cv_request, cv_data, cover_letter_data):
        """Create placeholder files (in production, these would be real PDFs/images)"""
        # This is a simplified placeholder - in production you'd generate actual files
        pass
