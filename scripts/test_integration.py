#!/usr/bin/env python
"""
Integration test script to verify all components work together properly.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import CandidateProfile, RecruiterProfile
from companies.models import Company
from jobs.models import Job
from applications.models import Application, ParsedResume
from talent_pool.models import TalentPool, JobMatch, CandidatePreferences
from background_verification.models import BackgroundCheckRequest
from job_matching_engine import JobMatchingEngine

User = get_user_model()

class IntegrationTester:
    def __init__(self):
        self.engine = JobMatchingEngine()
        self.test_results = []
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Running integration tests...")
        
        tests = [
            self.test_user_creation,
            self.test_job_matching_engine,
            self.test_talent_pool_integration,
            self.test_application_flow,
            self.test_resume_parsing_integration,
            self.test_background_verification_integration,
            self.test_ai_tools_integration,
            self.test_database_relationships,
            self.test_permissions_and_security
        ]
        
        for test in tests:
            try:
                test()
                self.test_results.append((test.__name__, True, None))
                print(f"  ✅ {test.__name__}")
            except Exception as e:
                self.test_results.append((test.__name__, False, str(e)))
                print(f"  ❌ {test.__name__}: {str(e)}")
        
        self.print_test_summary()
    
    def test_user_creation(self):
        """Test user creation and profile setup"""
        # Test candidate creation
        candidate_user = User.objects.filter(user_type='candidate').first()
        assert candidate_user is not None, "No candidate users found"
        assert hasattr(candidate_user, 'candidate_profile'), "Candidate profile not created"
        
        # Test recruiter creation
        recruiter_user = User.objects.filter(user_type='recruiter').first()
        assert recruiter_user is not None, "No recruiter users found"
        assert hasattr(recruiter_user, 'recruiter_profile'), "Recruiter profile not created"
        assert recruiter_user.recruiter_profile.company is not None, "Recruiter not linked to company"
    
    def test_job_matching_engine(self):
        """Test the job matching algorithm"""
        candidate_data = {
            'skills': ['Python', 'Django', 'React'],
            'total_experience_years': 3,
            'location': 'San Francisco, CA',
            'education': [],
            'preferences': {}
        }
        
        job_data = {
            'required_skills': ['Python', 'Django'],
            'preferred_skills': ['React', 'AWS'],
            'min_experience': 2,
            'max_experience': 5,
            'location': 'San Francisco, CA',
            'remote_ok': True,
            'salary_min': 80000,
            'job_type': 'full-time'
        }
        
        result = self.engine.calculate_comprehensive_match(candidate_data, job_data)
        
        assert 'overall_score' in result, "Overall score not calculated"
        assert result['overall_score'] > 0, "Match score should be positive"
        assert 'matched_skills' in result, "Matched skills not identified"
        assert 'ai_recommendation' in result, "AI recommendation not generated"
    
    def test_talent_pool_integration(self):
        """Test talent pool functionality"""
        # Check if talent pools exist
        pools = TalentPool.objects.all()
        assert pools.exists(), "No talent pools found"
        
        # Check if candidates are added to pools
        pool = pools.first()
        assert pool.candidates.exists(), "No candidates in talent pools"
        
        # Test match score calculation
        pool_candidate = pool.candidates.first()
        assert pool_candidate.match_score > 0, "Match score not calculated for pool candidate"
    
    def test_application_flow(self):
        """Test job application workflow"""
        applications = Application.objects.all()
        assert applications.exists(), "No applications found"
        
        application = applications.first()
        assert application.candidate is not None, "Application not linked to candidate"
        assert application.job is not None, "Application not linked to job"
        assert application.status in dict(Application.STATUS_CHOICES), "Invalid application status"
    
    def test_resume_parsing_integration(self):
        """Test resume parsing functionality"""
        parsed_resumes = ParsedResume.objects.all()
        if parsed_resumes.exists():
            resume = parsed_resumes.first()
            assert resume.application is not None, "Parsed resume not linked to application"
            assert resume.skill_match_percentage >= 0, "Skill match percentage not calculated"
    
    def test_background_verification_integration(self):
        """Test background verification system"""
        from background_verification.models import BackgroundCheckPackage
        
        packages = BackgroundCheckPackage.objects.all()
        assert packages.exists(), "No background check packages found"
        
        package = packages.first()
        assert package.included_checks, "Package has no included checks"
        assert package.estimated_cost > 0, "Package cost not set"
    
    def test_ai_tools_integration(self):
        """Test AI tools functionality"""
        from ai_tools.models import CVGenerationRequest
        
        # Test that AI tools models are accessible
        assert CVGenerationRequest._meta.get_field('user'), "CVGenerationRequest user field missing"
        assert CVGenerationRequest._meta.get_field('status'), "CVGenerationRequest status field missing"
    
    def test_database_relationships(self):
        """Test database relationships and foreign keys"""
        # Test Company -> RecruiterProfile relationship
        company = Company.objects.first()
        if company:
            recruiters = company.recruiter_profiles.all()
            for recruiter in recruiters:
                assert recruiter.company == company, "Recruiter-Company relationship broken"
        
        # Test Job -> Application relationship
        job = Job.objects.first()
        if job:
            applications = job.applications.all()
            for application in applications:
                assert application.job == job, "Job-Application relationship broken"
        
        # Test User -> Profile relationships
        users = User.objects.all()
        for user in users:
            if user.user_type == 'candidate':
                assert hasattr(user, 'candidate_profile'), f"Candidate profile missing for {user.email}"
            elif user.user_type == 'recruiter':
                assert hasattr(user, 'recruiter_profile'), f"Recruiter profile missing for {user.email}"
    
    def test_permissions_and_security(self):
        """Test basic permission and security checks"""
        # Test that sensitive fields are not exposed
        candidate = CandidateProfile.objects.first()
        if candidate:
            assert candidate.user.password.startswith('pbkdf2_'), "Password not properly hashed"
        
        # Test that required fields are set
        jobs = Job.objects.all()
        for job in jobs:
            assert job.title, "Job title is required"
            assert job.company, "Job must be linked to company"
            assert job.recruiter, "Job must be linked to recruiter"
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("🧪 INTEGRATION TEST RESULTS")
        print("="*60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! The system is fully integrated.")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")
            print("\nFailed Tests:")
            for test_name, success, error in self.test_results:
                if not success:
                    print(f"  ❌ {test_name}: {error}")
        
        print("="*60)

if __name__ == '__main__':
    tester = IntegrationTester()
    tester.run_all_tests()
