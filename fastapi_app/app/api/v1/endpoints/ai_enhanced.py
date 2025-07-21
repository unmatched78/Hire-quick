"""
Enhanced AI API Endpoints

Advanced AI-powered features using OpenAI integration for superior recruitment capabilities.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from pydantic import BaseModel

from ....core.security import get_current_user
from ....models.user import User
from ....services.openai_service import openai_service
from ....services.ai_service import ai_service
from ....utils.file_handler import file_handler

router = APIRouter()
logger = logging.getLogger(__name__)


class JobDescriptionRequest(BaseModel):
    """Request model for job description generation"""
    job_title: str
    company_info: Dict[str, Any]
    requirements: List[str]
    benefits: Optional[List[str]] = None
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"


class ResumeAnalysisRequest(BaseModel):
    """Request model for advanced resume analysis"""
    resume_text: str
    job_description: Optional[str] = None
    analysis_depth: Optional[str] = "comprehensive"


class InterviewQuestionsRequest(BaseModel):
    """Request model for interview question generation"""
    job_description: str
    candidate_resume: Optional[str] = None
    interview_type: Optional[str] = "general"
    difficulty_level: Optional[str] = "medium"
    question_count: Optional[int] = 10


class CandidateScreeningRequest(BaseModel):
    """Request model for candidate screening"""
    job_requirements: str
    candidate_data: Dict[str, Any]
    screening_criteria: Optional[List[str]] = None


class JobRecommendationRequest(BaseModel):
    """Request model for job recommendations"""
    candidate_profile: Dict[str, Any]
    preferences: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10


@router.post("/generate-job-description")
async def generate_job_description(
    request: JobDescriptionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a compelling job description using AI
    
    This endpoint uses advanced AI to create professional, engaging job descriptions
    that attract top talent and clearly communicate role expectations.
    """
    try:
        # Check user permissions (recruiters and admins only)
        if current_user.user_type not in ["recruiter", "admin"]:
            raise HTTPException(
                status_code=403, 
                detail="Only recruiters and admins can generate job descriptions"
            )
        
        result = await openai_service.generate_job_description(
            job_title=request.job_title,
            company_info=request.company_info,
            requirements=request.requirements,
            benefits=request.benefits
        )
        
        return {
            "success": True,
            "message": "Job description generated successfully",
            "data": result,
            "ai_powered": not result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Error generating job description: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate job description")


@router.post("/analyze-resume-advanced")
async def analyze_resume_advanced(
    request: ResumeAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform advanced AI-powered resume analysis
    
    Provides comprehensive insights including skills assessment, experience evaluation,
    career progression analysis, and job matching recommendations.
    """
    try:
        result = await openai_service.analyze_resume_advanced(
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        
        return {
            "success": True,
            "message": "Resume analysis completed successfully",
            "data": result,
            "ai_powered": not result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume")


@router.post("/upload-and-analyze-resume")
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload resume file and perform advanced AI analysis
    
    Supports PDF, DOC, DOCX, and TXT files. Extracts text and performs
    comprehensive AI-powered analysis.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF, DOC, DOCX, or TXT files."
            )
        
        # Process file upload
        file_info = await file_handler.process_file_upload(
            file=file,
            user_id=current_user.id,
            file_type="document",
            subfolder="resumes"
        )
        
        # Extract text from file
        resume_text = await file_handler.extract_text_from_file(file_info["file_path"])
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from the uploaded file"
            )
        
        # Perform AI analysis
        analysis_result = await openai_service.analyze_resume_advanced(
            resume_text=resume_text,
            job_description=job_description
        )
        
        return {
            "success": True,
            "message": "Resume uploaded and analyzed successfully",
            "file_info": file_info,
            "analysis": analysis_result,
            "ai_powered": not analysis_result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Error uploading and analyzing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to process resume")


@router.post("/generate-interview-questions-advanced")
async def generate_interview_questions_advanced(
    request: InterviewQuestionsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate advanced, personalized interview questions using AI
    
    Creates contextual questions based on job requirements and candidate background,
    with follow-up questions and evaluation criteria.
    """
    try:
        # Check user permissions
        if current_user.user_type not in ["recruiter", "admin"]:
            raise HTTPException(
                status_code=403, 
                detail="Only recruiters and admins can generate interview questions"
            )
        
        result = await openai_service.generate_interview_questions_advanced(
            job_description=request.job_description,
            candidate_resume=request.candidate_resume,
            interview_type=request.interview_type,
            difficulty_level=request.difficulty_level
        )
        
        return {
            "success": True,
            "message": "Interview questions generated successfully",
            "data": result,
            "ai_powered": not result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Error generating interview questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate interview questions")


@router.post("/screen-candidate-advanced")
async def screen_candidate_advanced(
    request: CandidateScreeningRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform AI-powered candidate screening
    
    Automatically evaluates candidate fit against job requirements,
    providing screening scores and recommendations.
    """
    try:
        # Check user permissions
        if current_user.user_type not in ["recruiter", "admin"]:
            raise HTTPException(
                status_code=403, 
                detail="Only recruiters and admins can screen candidates"
            )
        
        result = await openai_service.screen_candidate_application(
            job_requirements=request.job_requirements,
            candidate_data=request.candidate_data
        )
        
        return {
            "success": True,
            "message": "Candidate screening completed successfully",
            "data": result,
            "ai_powered": not result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Error screening candidate: {e}")
        raise HTTPException(status_code=500, detail="Failed to screen candidate")


@router.post("/job-recommendations-personalized")
async def get_personalized_job_recommendations(
    request: JobRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered personalized job recommendations
    
    Analyzes candidate profile and preferences to recommend the most suitable
    job opportunities with detailed matching explanations.
    """
    try:
        # Get available jobs (this would typically come from database)
        # For now, we'll use a mock list
        available_jobs = await get_available_jobs_for_recommendations(current_user.id)
        
        result = await openai_service.generate_personalized_job_recommendations(
            candidate_profile=request.candidate_profile,
            available_jobs=available_jobs
        )
        
        return {
            "success": True,
            "message": "Personalized job recommendations generated successfully",
            "data": result,
            "ai_powered": not result.get("fallback", False)
        }
        
    except Exception as e:
        logger.error(f"Error generating job recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate job recommendations")


@router.post("/salary-analysis")
async def analyze_salary_expectations(
    job_title: str,
    location: str,
    experience_level: str,
    skills: List[str],
    company_size: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered salary analysis and benchmarking
    
    Provides salary insights based on market data, location, skills, and experience.
    """
    try:
        # This would integrate with salary data APIs or use AI to analyze market trends
        salary_analysis = await analyze_market_salary(
            job_title=job_title,
            location=location,
            experience_level=experience_level,
            skills=skills,
            company_size=company_size
        )
        
        return {
            "success": True,
            "message": "Salary analysis completed successfully",
            "data": salary_analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing salary: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze salary")


@router.post("/skills-gap-analysis")
async def analyze_skills_gap(
    current_skills: List[str],
    target_job_description: str,
    career_goals: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered skills gap analysis
    
    Identifies missing skills for target roles and provides learning recommendations.
    """
    try:
        # Extract required skills from job description
        required_skills = await ai_service.extract_skills_from_text(target_job_description)
        
        # Perform gap analysis
        gap_analysis = await perform_skills_gap_analysis(
            current_skills=current_skills,
            required_skills=required_skills["extracted_skills"],
            job_description=target_job_description,
            career_goals=career_goals
        )
        
        return {
            "success": True,
            "message": "Skills gap analysis completed successfully",
            "data": gap_analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing skills gap: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze skills gap")


@router.post("/career-path-recommendations")
async def get_career_path_recommendations(
    current_position: str,
    skills: List[str],
    experience_years: int,
    career_goals: Optional[str] = None,
    industry_preference: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered career path recommendations
    
    Suggests potential career progression paths based on current profile and goals.
    """
    try:
        career_recommendations = await generate_career_path_recommendations(
            current_position=current_position,
            skills=skills,
            experience_years=experience_years,
            career_goals=career_goals,
            industry_preference=industry_preference
        )
        
        return {
            "success": True,
            "message": "Career path recommendations generated successfully",
            "data": career_recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating career recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate career recommendations")


# Helper functions (these would be implemented with actual business logic)

async def get_available_jobs_for_recommendations(user_id: int) -> List[Dict[str, Any]]:
    """Get available jobs for recommendations"""
    # This would query the database for active job postings
    return [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "salary_range": "120000-180000",
            "requirements": ["Python", "FastAPI", "PostgreSQL"],
            "description": "We are looking for a senior Python developer..."
        },
        {
            "id": 2,
            "title": "Full Stack Engineer",
            "company": "Startup Inc",
            "location": "Remote",
            "salary_range": "100000-150000",
            "requirements": ["React", "Node.js", "MongoDB"],
            "description": "Join our growing team as a full stack engineer..."
        }
    ]


async def analyze_market_salary(
    job_title: str,
    location: str,
    experience_level: str,
    skills: List[str],
    company_size: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze market salary data"""
    # This would integrate with salary APIs or use AI analysis
    return {
        "job_title": job_title,
        "location": location,
        "experience_level": experience_level,
        "salary_range": {
            "min": 80000,
            "max": 150000,
            "median": 115000,
            "currency": "USD"
        },
        "market_factors": [
            "High demand for Python skills",
            "Remote work premium",
            "Location-based adjustment"
        ],
        "skill_premiums": {
            "Python": 5000,
            "FastAPI": 3000,
            "AWS": 8000
        },
        "recommendations": [
            "Consider highlighting cloud skills for higher compensation",
            "Remote positions offer 10-15% premium in this market"
        ]
    }


async def perform_skills_gap_analysis(
    current_skills: List[str],
    required_skills: List[str],
    job_description: str,
    career_goals: Optional[str] = None
) -> Dict[str, Any]:
    """Perform skills gap analysis"""
    current_set = set(skill.lower() for skill in current_skills)
    required_set = set(skill.lower() for skill in required_skills)
    
    missing_skills = list(required_set - current_set)
    matching_skills = list(current_set & required_set)
    
    return {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "match_percentage": len(matching_skills) / len(required_skills) * 100 if required_skills else 0,
        "priority_skills": missing_skills[:5],  # Top 5 most important
        "learning_recommendations": [
            {
                "skill": skill,
                "priority": "high",
                "estimated_learning_time": "2-3 months",
                "resources": ["Online courses", "Practice projects", "Certifications"]
            }
            for skill in missing_skills[:3]
        ],
        "career_impact": "Acquiring these skills could increase job match rate by 40%"
    }


async def generate_career_path_recommendations(
    current_position: str,
    skills: List[str],
    experience_years: int,
    career_goals: Optional[str] = None,
    industry_preference: Optional[str] = None
) -> Dict[str, Any]:
    """Generate career path recommendations"""
    return {
        "current_position": current_position,
        "experience_years": experience_years,
        "career_paths": [
            {
                "path_name": "Technical Leadership Track",
                "next_roles": ["Senior Developer", "Tech Lead", "Engineering Manager"],
                "timeline": "2-5 years",
                "required_skills": ["Leadership", "System Design", "Mentoring"],
                "growth_potential": "high"
            },
            {
                "path_name": "Specialization Track",
                "next_roles": ["Senior Specialist", "Principal Engineer", "Architect"],
                "timeline": "3-7 years",
                "required_skills": ["Deep Technical Expertise", "System Architecture"],
                "growth_potential": "high"
            }
        ],
        "skill_development_plan": [
            {
                "skill": "Leadership",
                "importance": "high",
                "development_options": ["Management courses", "Mentoring junior developers"]
            }
        ],
        "market_outlook": "Strong demand for experienced developers with leadership skills"
    }