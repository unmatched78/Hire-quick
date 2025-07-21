"""
Comprehensive API Test Suite

Tests all the implemented features including AI, analytics, and file management.
"""

import asyncio
import httpx
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:12000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
RECRUITER_EMAIL = "recruiter@example.com"
RECRUITER_PASSWORD = "recruiterpass123"

class ComprehensiveAPITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.candidate_token = None
        self.recruiter_token = None
        self.test_job_id = None
        self.test_application_id = None
        self.test_company_id = None

    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 50)
        
        try:
            # Basic health checks
            await self.test_health_check()
            await self.test_root_endpoint()
            
            # Authentication tests
            await self.test_user_registration()
            await self.test_user_login()
            
            # User profile tests
            await self.test_user_profiles()
            
            # Company tests
            await self.test_company_management()
            
            # Job tests
            await self.test_job_management()
            
            # Application tests
            await self.test_application_management()
            
            # File management tests
            await self.test_file_management()
            
            # AI features tests
            await self.test_ai_features()
            
            # Analytics tests
            await self.test_analytics()
            
            print("\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            raise
        finally:
            await self.client.aclose()

    async def test_health_check(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Check...")
        
        response = await self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "features" in data
        
        print("✅ Health check passed")

    async def test_root_endpoint(self):
        """Test root endpoint"""
        print("\n🔍 Testing Root Endpoint...")
        
        response = await self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data
        
        print("✅ Root endpoint passed")

    async def test_user_registration(self):
        """Test user registration"""
        print("\n🔍 Testing User Registration...")
        
        # Register candidate
        candidate_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "user_type": "candidate",
            "first_name": "Test",
            "last_name": "Candidate"
        }
        
        response = await self.client.post("/api/v1/auth/register", json=candidate_data)
        assert response.status_code == 201
        
        # Register recruiter
        recruiter_data = {
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD,
            "user_type": "recruiter",
            "first_name": "Test",
            "last_name": "Recruiter"
        }
        
        response = await self.client.post("/api/v1/auth/register", json=recruiter_data)
        assert response.status_code == 201
        
        print("✅ User registration passed")

    async def test_user_login(self):
        """Test user login"""
        print("\n🔍 Testing User Login...")
        
        # Login candidate
        login_data = {
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = await self.client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        self.candidate_token = data["access_token"]
        assert self.candidate_token is not None
        
        # Login recruiter
        recruiter_login_data = {
            "username": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        }
        
        response = await self.client.post("/api/v1/auth/login", data=recruiter_login_data)
        assert response.status_code == 200
        
        data = response.json()
        self.recruiter_token = data["access_token"]
        assert self.recruiter_token is not None
        
        print("✅ User login passed")

    async def test_user_profiles(self):
        """Test user profile management"""
        print("\n🔍 Testing User Profiles...")
        
        # Test candidate profile
        headers = {"Authorization": f"Bearer {self.candidate_token}"}
        
        # Get current profile
        response = await self.client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        
        # Update candidate profile
        profile_data = {
            "skills": ["Python", "FastAPI", "React"],
            "experience_level": "mid",
            "location": "San Francisco, CA",
            "bio": "Experienced software developer"
        }
        
        response = await self.client.put("/api/v1/users/candidate-profile", json=profile_data, headers=headers)
        assert response.status_code == 200
        
        # Test recruiter profile
        recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        
        recruiter_profile_data = {
            "company_name": "Test Company",
            "position": "Senior Recruiter",
            "location": "New York, NY"
        }
        
        response = await self.client.put("/api/v1/users/recruiter-profile", json=recruiter_profile_data, headers=recruiter_headers)
        assert response.status_code == 200
        
        print("✅ User profiles passed")

    async def test_company_management(self):
        """Test company management"""
        print("\n🔍 Testing Company Management...")
        
        headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        
        # Create company
        company_data = {
            "name": "Test Tech Company",
            "description": "A leading technology company",
            "industry": "technology",
            "company_size": "medium",
            "location": "San Francisco, CA",
            "website": "https://testtech.com",
            "founded_year": 2020
        }
        
        response = await self.client.post("/api/v1/companies/", json=company_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        self.test_company_id = data["id"]
        
        # Get company
        response = await self.client.get(f"/api/v1/companies/{self.test_company_id}")
        assert response.status_code == 200
        
        # List companies
        response = await self.client.get("/api/v1/companies/")
        assert response.status_code == 200
        
        print("✅ Company management passed")

    async def test_job_management(self):
        """Test job management"""
        print("\n🔍 Testing Job Management...")
        
        headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        
        # Create job
        job_data = {
            "title": "Senior Python Developer",
            "description": "We are looking for an experienced Python developer to join our team.",
            "requirements": "5+ years of Python experience, FastAPI knowledge, database skills",
            "job_type": "full_time",
            "experience_level": "senior",
            "work_location": "hybrid",
            "location": "San Francisco, CA",
            "salary_min": 120000,
            "salary_max": 180000,
            "currency": "USD",
            "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "benefits": "Health insurance, 401k, flexible hours"
        }
        
        response = await self.client.post("/api/v1/jobs/", json=job_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        self.test_job_id = data["id"]
        
        # Get job
        response = await self.client.get(f"/api/v1/jobs/{self.test_job_id}")
        assert response.status_code == 200
        
        # List jobs
        response = await self.client.get("/api/v1/jobs/")
        assert response.status_code == 200
        
        # Search jobs
        response = await self.client.get("/api/v1/jobs/?search=Python&job_type=full_time")
        assert response.status_code == 200
        
        print("✅ Job management passed")

    async def test_application_management(self):
        """Test application management"""
        print("\n🔍 Testing Application Management...")
        
        headers = {"Authorization": f"Bearer {self.candidate_token}"}
        
        # Apply for job
        application_data = {
            "job_id": self.test_job_id,
            "cover_letter": "I am very interested in this position and believe my skills align well with your requirements."
        }
        
        response = await self.client.post("/api/v1/applications/", json=application_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        self.test_application_id = data["id"]
        
        # Get application
        response = await self.client.get(f"/api/v1/applications/{self.test_application_id}", headers=headers)
        assert response.status_code == 200
        
        # List applications
        response = await self.client.get("/api/v1/applications/", headers=headers)
        assert response.status_code == 200
        
        # Update application status (as recruiter)
        recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        status_data = {
            "status": "under_review",
            "notes": "Application looks promising"
        }
        
        response = await self.client.put(f"/api/v1/applications/{self.test_application_id}/status", json=status_data, headers=recruiter_headers)
        assert response.status_code == 200
        
        print("✅ Application management passed")

    async def test_file_management(self):
        """Test file management features"""
        print("\n🔍 Testing File Management...")
        
        headers = {"Authorization": f"Bearer {self.candidate_token}"}
        
        # Create a test file
        test_content = "This is a test resume content with Python, FastAPI, and React skills."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            # Upload file
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("test_resume.txt", f, "text/plain")}
                data = {"file_type": "document", "subfolder": "resumes"}
                
                response = await self.client.post("/api/v1/files/upload", files=files, data=data, headers=headers)
                assert response.status_code == 200
                
                upload_data = response.json()
                assert "file_info" in upload_data
            
            # Upload resume with parsing
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("resume.txt", f, "text/plain")}
                data = {"parse_resume": "true"}
                
                response = await self.client.post("/api/v1/files/upload/resume", files=files, data=data, headers=headers)
                assert response.status_code == 200
                
                resume_data = response.json()
                assert "parsed_data" in resume_data
            
            # List user files
            response = await self.client.get("/api/v1/files/list", headers=headers)
            assert response.status_code == 200
            
            # Get storage usage
            response = await self.client.get("/api/v1/files/storage-usage", headers=headers)
            assert response.status_code == 200
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
        
        print("✅ File management passed")

    async def test_ai_features(self):
        """Test AI-powered features"""
        print("\n🔍 Testing AI Features...")
        
        headers = {"Authorization": f"Bearer {self.candidate_token}"}
        recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        
        # Test job match calculation
        match_data = {
            "job_id": self.test_job_id,
            "candidate_skills": ["Python", "FastAPI", "React", "PostgreSQL"]
        }
        
        response = await self.client.post("/api/v1/ai/job-match", data=match_data, headers=headers)
        assert response.status_code == 200
        
        match_result = response.json()
        assert "match_score" in match_result
        assert match_result["match_score"] >= 0
        
        # Test job recommendations
        response = await self.client.get("/api/v1/ai/job-recommendations?limit=5", headers=headers)
        assert response.status_code == 200
        
        recommendations = response.json()
        assert "recommendations" in recommendations
        
        # Test skills extraction
        text = "I have experience with Python, JavaScript, React, Node.js, and PostgreSQL databases."
        response = await self.client.get(f"/api/v1/ai/skills/extract?text={text}", headers=headers)
        assert response.status_code == 200
        
        skills_data = response.json()
        assert "extracted_skills" in skills_data
        assert len(skills_data["extracted_skills"]) > 0
        
        # Test experience level detection
        experience_text = "I have 5 years of experience as a senior software engineer leading development teams."
        response = await self.client.get(f"/api/v1/ai/experience-level/detect?text={experience_text}", headers=headers)
        assert response.status_code == 200
        
        level_data = response.json()
        assert "detected_level" in level_data
        
        # Test interview question generation
        question_data = {
            "job_id": self.test_job_id
        }
        
        response = await self.client.post("/api/v1/ai/generate-interview-questions", data=question_data, headers=recruiter_headers)
        assert response.status_code == 200
        
        questions_data = response.json()
        assert "questions" in questions_data
        assert len(questions_data["questions"]) > 0
        
        # Test mock interview
        mock_data = {
            "job_id": self.test_job_id,
            "difficulty": "medium"
        }
        
        response = await self.client.post("/api/v1/ai/mock-interview", data=mock_data, headers=headers)
        assert response.status_code == 200
        
        mock_result = response.json()
        assert "session_id" in mock_result
        assert "questions" in mock_result
        
        print("✅ AI features passed")

    async def test_analytics(self):
        """Test analytics and reporting"""
        print("\n🔍 Testing Analytics...")
        
        candidate_headers = {"Authorization": f"Bearer {self.candidate_token}"}
        recruiter_headers = {"Authorization": f"Bearer {self.recruiter_token}"}
        
        # Test candidate dashboard analytics
        response = await self.client.get("/api/v1/analytics/dashboard", headers=candidate_headers)
        assert response.status_code == 200
        
        candidate_stats = response.json()
        assert "user_type" in candidate_stats
        assert candidate_stats["user_type"] == "candidate"
        assert "stats" in candidate_stats
        
        # Test recruiter dashboard analytics
        response = await self.client.get("/api/v1/analytics/dashboard", headers=recruiter_headers)
        assert response.status_code == 200
        
        recruiter_stats = response.json()
        assert "user_type" in recruiter_stats
        assert recruiter_stats["user_type"] == "recruiter"
        
        # Test job analytics
        response = await self.client.get(f"/api/v1/analytics/jobs/{self.test_job_id}", headers=recruiter_headers)
        assert response.status_code == 200
        
        job_analytics = response.json()
        assert "total_applications" in job_analytics
        
        # Test application analytics
        response = await self.client.get("/api/v1/analytics/applications", headers=recruiter_headers)
        assert response.status_code == 200
        
        app_analytics = response.json()
        assert "total_applications" in app_analytics
        
        # Test skills demand analytics
        response = await self.client.get("/api/v1/analytics/skills-demand", headers=recruiter_headers)
        assert response.status_code == 200
        
        skills_analytics = response.json()
        assert "top_skills" in skills_analytics
        
        # Test report generation
        report_data = {"report_type": "monthly"}
        response = await self.client.post("/api/v1/analytics/reports/generate", params=report_data, headers=recruiter_headers)
        assert response.status_code == 200
        
        report_result = response.json()
        assert "task_id" in report_result
        assert "status" in report_result
        
        print("✅ Analytics passed")

    async def test_advanced_features(self):
        """Test advanced features"""
        print("\n🔍 Testing Advanced Features...")
        
        headers = {"Authorization": f"Bearer {self.candidate_token}"}
        
        # Test application quality analysis
        if self.test_application_id:
            analysis_data = {"application_id": self.test_application_id}
            response = await self.client.post("/api/v1/ai/analyze-application", data=analysis_data, headers=headers)
            assert response.status_code == 200
            
            analysis_result = response.json()
            assert "analysis" in analysis_result
        
        print("✅ Advanced features passed")


async def main():
    """Run the comprehensive test suite"""
    tester = ComprehensiveAPITester()
    
    try:
        await tester.run_all_tests()
        print("\n🎉 All comprehensive tests passed!")
        return True
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)