from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import CandidateProfile, RecruiterProfile
from companies.models import Company
from jobs.models import Job
from applications.models import Application
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up the database with sample data for the recruitment platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating new sample data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting database...')
            self.reset_database()

        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Create companies
            companies = self.create_companies()
            self.stdout.write(f'Created {len(companies)} companies')
            
            # Create users and profiles
            candidates, recruiters = self.create_users_and_profiles(companies)
            self.stdout.write(f'Created {len(candidates)} candidates and {len(recruiters)} recruiters')
            
            # Create jobs
            jobs = self.create_jobs(recruiters)
            self.stdout.write(f'Created {len(jobs)} jobs')
            
            # Create applications
            applications = self.create_applications(candidates, jobs)
            self.stdout.write(f'Created {len(applications)} applications')

        self.stdout.write(
            self.style.SUCCESS('Successfully set up database with sample data!')
        )

    def reset_database(self):
        """Reset all data"""
        Application.objects.all().delete()
        Job.objects.all().delete()
        CandidateProfile.objects.all().delete()
        RecruiterProfile.objects.all().delete()
        Company.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_companies(self):
        """Create sample companies"""
        companies_data = [
            {
                'name': 'TechCorp Inc.',
                'description': 'Leading technology company specializing in cloud solutions and AI.',
                'website': 'https://techcorp.com',
                'industry': 'Technology',
                'size': '1000+',
                'location': 'San Francisco, CA',
                'founded_year': 2010,
            },
            {
                'name': 'StartupXYZ',
                'description': 'Innovative startup disrupting the fintech industry.',
                'website': 'https://startupxyz.com',
                'industry': 'Fintech',
                'size': '11-50',
                'location': 'Remote',
                'founded_year': 2020,
            },
            {
                'name': 'Design Studio Pro',
                'description': 'Creative design agency working with Fortune 500 companies.',
                'website': 'https://designstudiopro.com',
                'industry': 'Design',
                'size': '51-200',
                'location': 'New York, NY',
                'founded_year': 2015,
            },
            {
                'name': 'DataCorp Analytics',
                'description': 'Data analytics and business intelligence solutions.',
                'website': 'https://datacorp.com',
                'industry': 'Analytics',
                'size': '201-1000',
                'location': 'Austin, TX',
                'founded_year': 2012,
            },
            {
                'name': 'CloudTech Solutions',
                'description': 'Cloud infrastructure and DevOps consulting.',
                'website': 'https://cloudtech.com',
                'industry': 'Technology',
                'size': '201-1000',
                'location': 'Seattle, WA',
                'founded_year': 2018,
            },
        ]

        companies = []
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults=company_data
            )
            companies.append(company)

        return companies

    def create_users_and_profiles(self, companies):
        """Create sample users and their profiles"""
        # Create candidates
        candidates_data = [
            {
                'username': 'alice_johnson',
                'email': 'alice.johnson@email.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'location': 'San Francisco, CA',
                'linkedin_url': 'https://linkedin.com/in/alicejohnson',
                'github_url': 'https://github.com/alicejohnson',
                'portfolio_url': 'https://alicejohnson.dev',
                'summary': 'Experienced software engineer with 5+ years in full-stack development. Passionate about building scalable web applications.',
                'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker'],
                'experience_years': 5,
                'current_title': 'Senior Software Engineer',
                'salary_expectation': 150000,
                'availability': 'Immediately',
            },
            {
                'username': 'bob_wilson',
                'email': 'bob.wilson@email.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'location': 'Austin, TX',
                'linkedin_url': 'https://linkedin.com/in/bobwilson',
                'github_url': 'https://github.com/bobwilson',
                'summary': 'Product manager with expertise in data-driven decision making and agile methodologies.',
                'skills': ['Product Strategy', 'Analytics', 'Agile', 'SQL', 'Python'],
                'experience_years': 7,
                'current_title': 'Senior Product Manager',
                'salary_expectation': 140000,
                'availability': '2 weeks notice',
            },
            {
                'username': 'carol_davis',
                'email': 'carol.davis@email.com',
                'first_name': 'Carol',
                'last_name': 'Davis',
                'location': 'New York, NY',
                'linkedin_url': 'https://linkedin.com/in/caroldavis',
                'portfolio_url': 'https://caroldavis.design',
                'summary': 'Creative UX designer with a passion for user-centered design and accessibility.',
                'skills': ['Figma', 'User Research', 'Prototyping', 'Adobe Creative Suite', 'Sketch'],
                'experience_years': 4,
                'current_title': 'UX Designer',
                'salary_expectation': 110000,
                'availability': '1 month notice',
            },
        ]

        candidates = []
        for candidate_data in candidates_data:
            user, created = User.objects.get_or_create(
                username=candidate_data['username'],
                defaults={
                    'email': candidate_data['email'],
                    'user_type': 'candidate',
                }
            )
            if created:
                user.set_password('password123')
                user.save()

            profile, created = CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': candidate_data['first_name'],
                    'last_name': candidate_data['last_name'],
                    'location': candidate_data['location'],
                    'linkedin_url': candidate_data.get('linkedin_url', ''),
                    'github_url': candidate_data.get('github_url', ''),
                    'portfolio_url': candidate_data.get('portfolio_url', ''),
                    'summary': candidate_data['summary'],
                    'skills': candidate_data['skills'],
                    'experience_years': candidate_data['experience_years'],
                    'current_title': candidate_data['current_title'],
                    'salary_expectation': candidate_data['salary_expectation'],
                    'availability': candidate_data['availability'],
                }
            )
            candidates.append(profile)

        # Create recruiters
        recruiters_data = [
            {
                'username': 'john_recruiter',
                'email': 'john.smith@techcorp.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'company': companies[0],  # TechCorp
                'title': 'Senior Technical Recruiter',
                'department': 'Human Resources',
            },
            {
                'username': 'sarah_recruiter',
                'email': 'sarah.johnson@startupxyz.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'company': companies[1],  # StartupXYZ
                'title': 'Talent Acquisition Manager',
                'department': 'People Operations',
            },
            {
                'username': 'mike_recruiter',
                'email': 'mike.davis@designstudio.com',
                'first_name': 'Mike',
                'last_name': 'Davis',
                'company': companies[2],  # Design Studio
                'title': 'Creative Talent Lead',
                'department': 'Design',
            },
        ]

        recruiters = []
        for recruiter_data in recruiters_data:
            user, created = User.objects.get_or_create(
                username=recruiter_data['username'],
                defaults={
                    'email': recruiter_data['email'],
                    'user_type': 'recruiter',
                }
            )
            if created:
                user.set_password('password123')
                user.save()

            profile, created = RecruiterProfile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': recruiter_data['first_name'],
                    'last_name': recruiter_data['last_name'],
                    'company': recruiter_data['company'],
                    'title': recruiter_data['title'],
                    'department': recruiter_data['department'],
                }
            )
            recruiters.append(profile)

        return candidates, recruiters

    def create_jobs(self, recruiters):
        """Create sample job postings"""
        jobs_data = [
            {
                'title': 'Senior Software Engineer',
                'recruiter': recruiters[0],  # John from TechCorp
                'description': '''We are looking for a Senior Software Engineer to join our growing engineering team. 
                
Key Responsibilities:
• Design and develop scalable web applications
• Collaborate with cross-functional teams
• Mentor junior developers
• Participate in code reviews and technical discussions
• Contribute to architectural decisions

Requirements:
• 5+ years of software development experience
• Strong proficiency in Python and JavaScript
• Experience with React and Node.js
• Knowledge of cloud platforms (AWS preferred)
• Excellent problem-solving skills''',
                'requirements': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS'],
                'preferred_skills': ['Docker', 'Kubernetes', 'TypeScript', 'GraphQL'],
                'location': 'San Francisco, CA',
                'job_type': 'full-time',
                'remote_ok': True,
                'salary_min': 120000,
                'salary_max': 180000,
                'experience_min': 5,
                'experience_max': 10,
                'education_required': 'Bachelor\'s degree in Computer Science or related field',
                'benefits': ['Health Insurance', '401k', 'Stock Options', 'Remote Work', 'Flexible Hours'],
            },
            {
                'title': 'Product Manager',
                'recruiter': recruiters[1],  # Sarah from StartupXYZ
                'description': '''Join our product team to drive innovation and growth in the fintech space.
                
Key Responsibilities:
• Define product strategy and roadmap
• Work closely with engineering and design teams
• Analyze user data and market trends
• Manage product launches and feature releases
• Collaborate with stakeholders across the organization

Requirements:
• 3+ years of product management experience
• Strong analytical and problem-solving skills
• Experience with agile methodologies
• Excellent communication skills
• Background in fintech or financial services preferred''',
                'requirements': ['Product Strategy', 'Analytics', 'Agile', 'Stakeholder Management'],
                'preferred_skills': ['SQL', 'Python', 'User Research', 'A/B Testing'],
                'location': 'Remote',
                'job_type': 'full-time',
                'remote_ok': True,
                'salary_min': 100000,
                'salary_max': 150000,
                'experience_min': 3,
                'experience_max': 8,
                'education_required': 'Bachelor\'s degree in Business, Engineering, or related field',
                'benefits': ['Health Insurance', 'Equity', 'Unlimited PTO', 'Learning Budget'],
            },
            {
                'title': 'UX Designer',
                'recruiter': recruiters[2],  # Mike from Design Studio
                'description': '''We're seeking a talented UX Designer to create beautiful and intuitive user experiences.
                
Key Responsibilities:
• Conduct user research and usability testing
• Create wireframes, prototypes, and design systems
• Collaborate with product and engineering teams
• Present design concepts to stakeholders
• Ensure accessibility and inclusive design practices

Requirements:
• 2+ years of UX design experience
• Proficiency in Figma and design tools
• Strong portfolio demonstrating UX process
• Understanding of user-centered design principles
• Experience with design systems''',
                'requirements': ['Figma', 'User Research', 'Prototyping', 'Design Systems'],
                'preferred_skills': ['Adobe Creative Suite', 'Sketch', 'InVision', 'HTML/CSS'],
                'location': 'New York, NY',
                'job_type': 'contract',
                'remote_ok': False,
                'salary_min': 80000,
                'salary_max': 120000,
                'experience_min': 2,
                'experience_max': 6,
                'education_required': 'Bachelor\'s degree in Design, HCI, or related field',
                'benefits': ['Health Insurance', 'Professional Development', 'Creative Freedom'],
            },
        ]

        jobs = []
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['recruiter'].company,
                defaults={
                    'recruiter': job_data['recruiter'],
                    'description': job_data['description'],
                    'requirements': job_data['requirements'],
                    'preferred_skills': job_data['preferred_skills'],
                    'location': job_data['location'],
                    'job_type': job_data['job_type'],
                    'remote_ok': job_data['remote_ok'],
                    'salary_min': job_data['salary_min'],
                    'salary_max': job_data['salary_max'],
                    'experience_min': job_data['experience_min'],
                    'experience_max': job_data['experience_max'],
                    'education_required': job_data['education_required'],
                    'benefits': job_data['benefits'],
                    'status': 'active',
                }
            )
            jobs.append(job)

        return jobs

    def create_applications(self, candidates, jobs):
        """Create sample applications"""
        applications_data = [
            {
                'job': jobs[0],  # Senior Software Engineer
                'candidate': candidates[0],  # Alice
                'status': 'interview',
                'cover_letter': '''Dear Hiring Manager,

I am excited to apply for the Senior Software Engineer position at TechCorp. With over 5 years of experience in full-stack development, I believe I would be a great fit for your team.

In my current role, I have successfully led the development of several scalable web applications using Python, React, and AWS. I am particularly drawn to TechCorp's innovative approach to cloud solutions and would love to contribute to your mission.

I look forward to discussing how my skills and experience can benefit your team.

Best regards,
Alice Johnson''',
            },
            {
                'job': jobs[1],  # Product Manager
                'candidate': candidates[1],  # Bob
                'status': 'screening',
                'cover_letter': '''Hello StartupXYZ Team,

I am writing to express my interest in the Product Manager position. With 7 years of product management experience, including 3 years in fintech, I am excited about the opportunity to drive innovation at StartupXYZ.

My experience in data-driven decision making and agile methodologies aligns perfectly with your requirements. I have successfully launched multiple products that have driven significant user growth and revenue.

I would welcome the opportunity to discuss how I can contribute to StartupXYZ's continued success.

Sincerely,
Bob Wilson''',
            },
            {
                'job': jobs[2],  # UX Designer
                'candidate': candidates[2],  # Carol
                'status': 'applied',
                'cover_letter': '''Dear Design Studio Pro,

I am thrilled to apply for the UX Designer position. As a passionate advocate for user-centered design, I am impressed by your portfolio of work with Fortune 500 companies.

My 4 years of experience in UX design, combined with my expertise in Figma and user research, make me well-suited for this role. I have a proven track record of creating intuitive designs that improve user satisfaction and business metrics.

I would love to bring my creativity and user advocacy to your team.

Best regards,
Carol Davis''',
            },
        ]

        applications = []
        for app_data in applications_data:
            application, created = Application.objects.get_or_create(
                job=app_data['job'],
                candidate=app_data['candidate'],
                defaults={
                    'status': app_data['status'],
                    'cover_letter': app_data['cover_letter'],
                }
            )
            applications.append(application)

        return applications
