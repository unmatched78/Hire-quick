#!/usr/bin/env python
"""
Complete database setup script for the recruitment platform.
This script sets up all necessary database tables, creates sample data,
and ensures all integrations work properly.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import User, CandidateProfile, RecruiterProfile
from companies.models import Company
from jobs.models import Job, ApplicationFormField
from applications.models import Application, ParsedResume
from talent_pool.models import TalentPool, TalentPoolCandidate, JobMatch, CandidatePreferences
from background_verification.models import BackgroundCheckPackage
from ai_tools.models import CVGenerationRequest

User = get_user_model()

class DatabaseSetup:
    def __init__(self):
        self.companies = []
        self.recruiters = []
        self.candidates = []
        self.jobs = []
        self.talent_pools = []
        
    def run_setup(self):
        """Run complete database setup"""
        print("🚀 Starting complete database setup...")
        
        try:
            with transaction.atomic():
                self.create_companies()
                self.create_users()
                self.create_jobs()
                self.create_talent_pools()
                self.create_background_check_packages()
                self.create_sample_applications()
                self.create_job_matches()
                self.setup_candidate_preferences()
                
            print("✅ Database setup completed successfully!")
            self.print_summary()
            
        except Exception as e:
            print(f"❌ Error during setup: {str(e)}")
            raise
    
    def create_companies(self):
        """Create sample companies"""
        print("📊 Creating companies...")
        
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'description': 'Leading technology solutions provider',
                'industry': 'Technology',
                'size': 'large',
                'website': 'https://techcorp.com',
                'location': 'San Francisco, CA'
            },
            {
                'name': 'InnovateLabs',
                'description': 'Cutting-edge AI and ML research company',
                'industry': 'Artificial Intelligence',
                'size': 'medium',
                'website': 'https://innovatelabs.com',
                'location': 'Austin, TX'
            },
            {
                'name': 'StartupHub',
                'description': 'Fast-growing fintech startup',
                'industry': 'Financial Technology',
                'size': 'startup',
                'website': 'https://startuphub.com',
                'location': 'New York, NY'
            },
            {
                'name': 'GlobalSoft Inc',
                'description': 'Enterprise software solutions',
                'industry': 'Software',
                'size': 'large',
                'website': 'https://globalsoft.com',
                'location': 'Seattle, WA'
            }
        ]
        
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults=company_data
            )
            self.companies.append(company)
            if created:
                print(f"  ✓ Created company: {company.name}")
    
    def create_users(self):
        """Create sample users (recruiters and candidates)"""
        print("👥 Creating users...")
        
        # Create recruiters
        recruiters_data = [
            {
                'email': 'recruiter1@techcorp.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'company': self.companies[0],
                'title': 'Senior Technical Recruiter'
            },
            {
                'email': 'recruiter2@innovatelabs.com',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'company': self.companies[1],
                'title': 'Head of Talent Acquisition'
            },
            {
                'email': 'recruiter3@startuphub.com',
                'first_name': 'Emily',
                'last_name': 'Rodriguez',
                'company': self.companies[2],
                'title': 'Talent Partner'
            }
        ]
        
        for recruiter_data in recruiters_data:
            user, created = User.objects.get_or_create(
                email=recruiter_data['email'],
                defaults={
                    'first_name': recruiter_data['first_name'],
                    'last_name': recruiter_data['last_name'],
                    'user_type': 'recruiter',
                    'is_active': True,
                    'email_verified': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                recruiter_profile = RecruiterProfile.objects.create(
                    user=user,
                    company=recruiter_data['company'],
                    title=recruiter_data['title'],
                    profile_completed=True
                )
                self.recruiters.append(recruiter_profile)
                print(f"  ✓ Created recruiter: {user.get_full_name()}")
        
        # Create candidates
        candidates_data = [
            {
                'email': 'john.doe@email.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'current_title': 'Senior Python Developer',
                'location': 'San Francisco, CA',
                'experience_years': 5,
                'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'AWS', 'Docker'],
                'summary': 'Experienced full-stack developer with expertise in Python and modern web technologies.'
            },
            {
                'email': 'jane.smith@email.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'current_title': 'Data Scientist',
                'location': 'Austin, TX',
                'experience_years': 3,
                'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Pandas', 'SQL', 'R'],
                'summary': 'Data scientist passionate about machine learning and AI applications.'
            },
            {
                'email': 'alex.wilson@email.com',
                'first_name': 'Alex',
                'last_name': 'Wilson',
                'current_title': 'Frontend Developer',
                'location': 'New York, NY',
                'experience_years': 4,
                'skills': ['JavaScript', 'React', 'Vue.js', 'TypeScript', 'CSS', 'Node.js'],
                'summary': 'Creative frontend developer with a passion for user experience and modern web technologies.'
            },
            {
                'email': 'maria.garcia@email.com',
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'current_title': 'DevOps Engineer',
                'location': 'Seattle, WA',
                'experience_years': 6,
                'skills': ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'Jenkins', 'Python'],
                'summary': 'DevOps engineer specializing in cloud infrastructure and automation.'
            },
            {
                'email': 'david.brown@email.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'current_title': 'Full Stack Developer',
                'location': 'Remote',
                'experience_years': 2,
                'skills': ['JavaScript', 'Node.js', 'React', 'MongoDB', 'Express', 'Git'],
                'summary': 'Junior full-stack developer eager to grow and contribute to innovative projects.'
            }
        ]
        
        for candidate_data in candidates_data:
            user, created = User.objects.get_or_create(
                email=candidate_data['email'],
                defaults={
                    'first_name': candidate_data['first_name'],
                    'last_name': candidate_data['last_name'],
                    'user_type': 'candidate',
                    'is_active': True,
                    'email_verified': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                candidate_profile = CandidateProfile.objects.create(
                    user=user,
                    current_title=candidate_data['current_title'],
                    location=candidate_data['location'],
                    experience_years=candidate_data['experience_years'],
                    skills=candidate_data['skills'],
                    summary=candidate_data['summary'],
                    profile_completed=True
                )
                self.candidates.append(candidate_profile)
                print(f"  ✓ Created candidate: {user.get_full_name()}")
    
    def create_jobs(self):
        """Create sample job postings"""
        print("💼 Creating job postings...")
        
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'company': self.companies[0],
                'recruiter': self.recruiters[0],
                'description': 'We are looking for an experienced Python developer to join our backend team.',
                'requirements': ['Python', 'Django', 'PostgreSQL', 'REST APIs', 'Git'],
                'preferred_skills': ['AWS', 'Docker', 'Redis', 'Celery'],
                'location': 'San Francisco, CA',
                'job_type': 'full-time',
                'experience_min': 3,
                'experience_max': 7,
                'salary_min': 120000,
                'salary_max': 160000,
                'remote_ok': True,
                'status': 'active'
            },
            {
                'title': 'Machine Learning Engineer',
                'company': self.companies[1],
                'recruiter': self.recruiters[1],
                'description': 'Join our AI research team to develop cutting-edge ML solutions.',
                'requirements': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch'],
                'preferred_skills': ['MLOps', 'Kubernetes', 'AWS', 'Statistics'],
                'location': 'Austin, TX',
                'job_type': 'full-time',
                'experience_min': 2,
                'experience_max': 5,
                'salary_min': 110000,
                'salary_max': 150000,
                'remote_ok': True,
                'status': 'active'
            },
            {
                'title': 'Frontend Developer',
                'company': self.companies[2],
                'recruiter': self.recruiters[2],
                'description': 'Build amazing user interfaces for our fintech platform.',
                'requirements': ['JavaScript', 'React', 'CSS', 'HTML'],
                'preferred_skills': ['TypeScript', 'Redux', 'Webpack', 'Jest'],
                'location': 'New York, NY',
                'job_type': 'full-time',
                'experience_min': 2,
                'experience_max': 5,
                'salary_min': 90000,
                'salary_max': 130000,
                'remote_ok': False,
                'status': 'active'
            },
            {
                'title': 'DevOps Engineer',
                'company': self.companies[3],
                'recruiter': self.recruiters[0],
                'description': 'Manage and scale our cloud infrastructure.',
                'requirements': ['AWS', 'Docker', 'Kubernetes', 'Terraform'],
                'preferred_skills': ['Jenkins', 'Monitoring', 'Python', 'Bash'],
                'location': 'Seattle, WA',
                'job_type': 'full-time',
                'experience_min': 4,
                'experience_max': 8,
                'salary_min': 130000,
                'salary_max': 170000,
                'remote_ok': True,
                'status': 'active'
            },
            {
                'title': 'Junior Full Stack Developer',
                'company': self.companies[0],
                'recruiter': self.recruiters[0],
                'description': 'Great opportunity for a junior developer to grow with our team.',
                'requirements': ['JavaScript', 'Node.js', 'React', 'Git'],
                'preferred_skills': ['MongoDB', 'Express', 'Testing', 'Agile'],
                'location': 'San Francisco, CA',
                'job_type': 'full-time',
                'experience_min': 0,
                'experience_max': 3,
                'salary_min': 70000,
                'salary_max': 95000,
                'remote_ok': True,
                'status': 'active'
            }
        ]
        
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults=job_data
            )
            self.jobs.append(job)
            if created:
                print(f"  ✓ Created job: {job.title} at {job.company.name}")
    
    def create_talent_pools(self):
        """Create sample talent pools"""
        print("🎯 Creating talent pools...")
        
        pools_data = [
            {
                'name': 'Python Developers',
                'description': 'Pool of experienced Python developers',
                'pool_type': 'skill_based',
                'company': self.companies[0],
                'created_by': self.recruiters[0],
                'required_skills': ['Python', 'Django', 'Flask'],
                'preferred_skills': ['AWS', 'Docker', 'PostgreSQL'],
                'min_experience': 2,
                'max_experience': 10,
                'locations': ['San Francisco, CA', 'Remote']
            },
            {
                'name': 'AI/ML Specialists',
                'description': 'Machine learning and AI experts',
                'pool_type': 'skill_based',
                'company': self.companies[1],
                'created_by': self.recruiters[1],
                'required_skills': ['Machine Learning', 'Python', 'TensorFlow'],
                'preferred_skills': ['PyTorch', 'MLOps', 'Statistics'],
                'min_experience': 1,
                'max_experience': 8,
                'locations': ['Austin, TX', 'Remote']
            },
            {
                'name': 'Frontend Talent',
                'description': 'Frontend developers and UI/UX specialists',
                'pool_type': 'skill_based',
                'company': self.companies[2],
                'created_by': self.recruiters[2],
                'required_skills': ['JavaScript', 'React', 'CSS'],
                'preferred_skills': ['TypeScript', 'Vue.js', 'Design'],
                'min_experience': 1,
                'max_experience': 6,
                'locations': ['New York, NY']
            }
        ]
        
        for pool_data in pools_data:
            pool, created = TalentPool.objects.get_or_create(
                name=pool_data['name'],
                company=pool_data['company'],
                defaults=pool_data
            )
            self.talent_pools.append(pool)
            if created:
                print(f"  ✓ Created talent pool: {pool.name}")
                
                # Add candidates to pools based on skills
                self.add_candidates_to_pools(pool)
    
    def add_candidates_to_pools(self, pool):
        """Add relevant candidates to talent pools"""
        from job_matching_engine import JobMatchingEngine
        
        engine = JobMatchingEngine()
        
        for candidate in self.candidates:
            # Calculate match score
            candidate_data = {
                'skills': candidate.skills or [],
                'total_experience_years': candidate.experience_years,
                'location': candidate.location,
                'education': [],
                'preferences': {}
            }
            
            pool_data = {
                'required_skills': pool.required_skills,
                'preferred_skills': pool.preferred_skills,
                'min_experience': pool.min_experience,
                'max_experience': pool.max_experience,
                'location': pool.locations[0] if pool.locations else '',
                'remote_ok': 'remote' in [loc.lower() for loc in pool.locations] if pool.locations else False
            }
            
            match_result = engine.calculate_comprehensive_match(candidate_data, pool_data)
            
            # Add to pool if match score is above threshold
            if match_result['overall_score'] >= 60:
                TalentPoolCandidate.objects.get_or_create(
                    talent_pool=pool,
                    candidate=candidate,
                    defaults={
                        'added_by': pool.created_by,
                        'match_score': match_result['overall_score'],
                        'matched_skills': match_result['matched_skills'],
                        'missing_skills': match_result['missing_skills'],
                        'status': 'active',
                        'priority': 'high' if match_result['overall_score'] >= 80 else 'medium'
                    }
                )
                print(f"    ✓ Added {candidate.get_full_name()} to {pool.name} ({match_result['overall_score']:.1f}% match)")
    
    def create_background_check_packages(self):
        """Create background check packages"""
        print("🔍 Creating background check packages...")
        
        packages_data = [
            {
                'name': 'Basic Check',
                'description': 'Essential background verification',
                'included_checks': ['criminal', 'identity', 'employment'],
                'estimated_cost': 25.00,
                'estimated_turnaround_days': 3,
                'is_active': True
            },
            {
                'name': 'Standard Check',
                'description': 'Comprehensive background verification',
                'included_checks': ['criminal', 'identity', 'employment', 'education', 'reference'],
                'estimated_cost': 45.00,
                'estimated_turnaround_days': 5,
                'is_active': True
            },
            {
                'name': 'Premium Check',
                'description': 'Complete background verification with additional checks',
                'included_checks': ['criminal', 'identity', 'employment', 'education', 'reference', 'credit', 'driving'],
                'estimated_cost': 75.00,
                'estimated_turnaround_days': 7,
                'is_active': True
            }
        ]
        
        for package_data in packages_data:
            package, created = BackgroundCheckPackage.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            if created:
                print(f"  ✓ Created background check package: {package.name}")
    
    def create_sample_applications(self):
        """Create sample job applications"""
        print("📝 Creating sample applications...")
        
        # Create applications for some job-candidate combinations
        applications_data = [
            {'job': self.jobs[0], 'candidate': self.candidates[0], 'status': 'applied'},
            {'job': self.jobs[1], 'candidate': self.candidates[1], 'status': 'screening'},
            {'job': self.jobs[2], 'candidate': self.candidates[2], 'status': 'interview'},
            {'job': self.jobs[3], 'candidate': self.candidates[3], 'status': 'applied'},
            {'job': self.jobs[4], 'candidate': self.candidates[4], 'status': 'applied'},
        ]
        
        for app_data in applications_data:
            application, created = Application.objects.get_or_create(
                job=app_data['job'],
                candidate=app_data['candidate'],
                defaults={
                    'status': app_data['status'],
                    'form_responses': {},
                    'applied_at': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )
            if created:
                print(f"  ✓ Created application: {application.candidate.get_full_name()} -> {application.job.title}")
                
                # Create parsed resume for some applications
                if random.choice([True, False]):
                    self.create_parsed_resume(application)
    
    def create_parsed_resume(self, application):
        """Create sample parsed resume data"""
        candidate = application.candidate
        
        # Sample parsed resume data
        parsed_resume_data = {
            'full_name': candidate.get_full_name(),
            'email': candidate.user.email,
            'phone': '+1-555-0123',
            'linkedin_url': f'https://linkedin.com/in/{candidate.user.first_name.lower()}-{candidate.user.last_name.lower()}',
            'skills_data': {
                'programming': candidate.skills[:3] if candidate.skills else [],
                'frameworks': candidate.skills[3:6] if len(candidate.skills) > 3 else [],
                'tools': candidate.skills[6:] if len(candidate.skills) > 6 else []
            },
            'total_experience_years': candidate.experience_years,
            'experience_data': [
                {
                    'title': candidate.current_title,
                    'company': 'Previous Company',
                    'duration': f'{candidate.experience_years} years',
                    'description': 'Worked on various projects using modern technologies.'
                }
            ],
            'education_data': [
                {
                    'degree': 'Bachelor of Computer Science',
                    'institution': 'University of Technology',
                    'year': '2018'
                }
            ],
            'skill_match_percentage': random.uniform(60, 95),
            'ai_score': random.uniform(70, 90),
            'career_level': 'Mid-level' if candidate.experience_years >= 3 else 'Junior'
        }
        
        ParsedResume.objects.get_or_create(
            application=application,
            defaults=parsed_resume_data
        )
    
    def create_job_matches(self):
        """Create job matches for candidates"""
        print("🎯 Creating job matches...")
        
        from job_matching_engine import JobMatchingEngine
        engine = JobMatchingEngine()
        
        matches_created = 0
        
        for candidate in self.candidates:
            for job in self.jobs:
                # Skip if already applied
                if Application.objects.filter(candidate=candidate, job=job).exists():
                    continue
                
                # Prepare data for matching
                candidate_data = {
                    'skills': candidate.skills or [],
                    'total_experience_years': candidate.experience_years,
                    'location': candidate.location,
                    'education': [],
                    'preferences': {}
                }
                
                job_data = {
                    'title': job.title,
                    'required_skills': job.requirements or [],
                    'preferred_skills': job.preferred_skills or [],
                    'min_experience': job.experience_min,
                    'max_experience': job.experience_max,
                    'location': job.location,
                    'remote_ok': job.remote_ok,
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'job_type': job.job_type
                }
                
                # Calculate match
                match_result = engine.calculate_comprehensive_match(candidate_data, job_data)
                
                # Create match if score is above threshold
                if match_result['overall_score'] >= 50:
                    JobMatch.objects.get_or_create(
                        candidate=candidate,
                        job=job,
                        defaults={
                            'match_type': 'auto',
                            'overall_score': match_result['overall_score'],
                            'skill_score': match_result['skill_score'],
                            'experience_score': match_result['experience_score'],
                            'location_score': match_result['location_score'],
                            'education_score': match_result['education_score'],
                            'matched_skills': match_result['matched_skills'],
                            'missing_skills': match_result['missing_skills'],
                            'match_reasons': match_result['match_reasons'],
                            'ai_recommendation': match_result['ai_recommendation'],
                            'fit_analysis': match_result['fit_analysis'],
                            'expires_at': timezone.now() + timedelta(days=30)
                        }
                    )
                    matches_created += 1
        
        print(f"  ✓ Created {matches_created} job matches")
    
    def setup_candidate_preferences(self):
        """Setup candidate job preferences"""
        print("⚙️ Setting up candidate preferences...")
        
        preferences_data = [
            {
                'candidate': self.candidates[0],
                'job_types': ['full-time'],
                'preferred_roles': ['Senior Developer', 'Lead Developer', 'Tech Lead'],
                'remote_preference': 'preferred',
                'min_salary': 110000,
                'max_salary': 170000,
                'willing_to_relocate': True
            },
            {
                'candidate': self.candidates[1],
                'job_types': ['full-time', 'contract'],
                'preferred_roles': ['Data Scientist', 'ML Engineer', 'AI Researcher'],
                'remote_preference': 'required',
                'min_salary': 100000,
                'max_salary': 160000,
                'willing_to_relocate': False
            },
            {
                'candidate': self.candidates[2],
                'job_types': ['full-time'],
                'preferred_roles': ['Frontend Developer', 'UI Developer', 'React Developer'],
                'remote_preference': 'hybrid',
                'min_salary': 80000,
                'max_salary': 140000,
                'willing_to_relocate': True
            }
        ]
        
        for pref_data in preferences_data:
            candidate = pref_data.pop('candidate')
            CandidatePreferences.objects.get_or_create(
                candidate=candidate,
                defaults=pref_data
            )
            print(f"  ✓ Set preferences for {candidate.get_full_name()}")
    
    def print_summary(self):
        """Print setup summary"""
        print("\n" + "="*50)
        print("📊 DATABASE SETUP SUMMARY")
        print("="*50)
        print(f"Companies: {len(self.companies)}")
        print(f"Recruiters: {len(self.recruiters)}")
        print(f"Candidates: {len(self.candidates)}")
        print(f"Jobs: {len(self.jobs)}")
        print(f"Talent Pools: {len(self.talent_pools)}")
        print(f"Applications: {Application.objects.count()}")
        print(f"Job Matches: {JobMatch.objects.count()}")
        print(f"Background Check Packages: {BackgroundCheckPackage.objects.count()}")
        print("\n🔐 LOGIN CREDENTIALS:")
        print("Recruiters:")
        for recruiter in self.recruiters:
            print(f"  📧 {recruiter.user.email} | 🔑 password123")
        print("\nCandidates:")
        for candidate in self.candidates:
            print(f"  📧 {candidate.user.email} | 🔑 password123")
        print("\n🌐 Access the platform at: http://localhost:8000")
        print("="*50)

if __name__ == '__main__':
    import random
    setup = DatabaseSetup()
    setup.run_setup()
