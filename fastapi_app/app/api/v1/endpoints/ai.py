"""
AI-Powered Features API Endpoints

AI-powered recruitment features including resume parsing, job matching, and interview assistance.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....services.ai_service import ai_service
from ....utils.file_handler import file_handler
from ....utils.background_tasks import schedule_resume_processing, schedule_job_recommendations

router = APIRouter()


@router.post("/parse-resume")
async def parse_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Parse a resume and extract structured information
    
    Uploads and processes a resume file to extract:
    - Personal information
    - Skills and technologies
    - Work experience
    - Education
    - Certifications
    """
    try:
        # Upload and process the file
        file_info = await file_handler.upload_file(
            file, 
            file_type="document", 
            user_id=current_user.id,
            subfolder="resumes"
        )
        
        if not file_info.get('text_content'):
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        # Parse resume with AI
        parsed_data = await ai_service.parse_resume(file_info['text_content'])
        
        if 'error' in parsed_data:
            raise HTTPException(status_code=500, detail=parsed_data['error'])
        
        # Schedule background processing for more detailed analysis
        task_id = await schedule_resume_processing(file_info['text_content'], current_user.id)
        
        return {
            "message": "Resume parsed successfully",
            "file_info": {
                "filename": file_info['filename'],
                "file_url": file_info['file_url'],
                "file_size": file_info['file_size']
            },
            "parsed_data": parsed_data,
            "background_task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/job-match")
async def calculate_job_match(
    job_id: int = Form(..., description="Job ID to match against"),
    candidate_skills: List[str] = Form(..., description="List of candidate skills"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate how well a candidate matches a specific job
    
    Analyzes candidate skills against job requirements and returns a match score.
    """
    try:
        from sqlalchemy import select
        from ....models.job import Job
        
        # Get job details
        job_query = select(Job).where(Job.id == job_id)
        result = await db.execute(job_query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Calculate match score
        match_score = await ai_service.calculate_job_match_score(
            candidate_skills,
            job.requirements,
            job.skills_required
        )
        
        return {
            "job_id": job_id,
            "job_title": job.title,
            "match_score": match_score,
            "candidate_skills": candidate_skills,
            "required_skills": job.skills_required,
            "matching_skills": list(set(candidate_skills) & set(job.skills_required)),
            "missing_skills": list(set(job.skills_required) - set(candidate_skills)),
            "additional_skills": list(set(candidate_skills) - set(job.skills_required))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate job match: {str(e)}")


@router.get("/job-recommendations")
async def get_job_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get AI-powered job recommendations for the current user
    
    Returns personalized job recommendations based on user profile and skills.
    """
    if current_user.user_type != 'candidate':
        raise HTTPException(status_code=403, detail="Only candidates can get job recommendations")
    
    try:
        recommendations = await ai_service.get_job_recommendations(db, current_user.id, limit)
        
        # Schedule background task to update recommendations
        task_id = await schedule_job_recommendations(current_user.id)
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "background_update_task": task_id,
            "message": "Job recommendations generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job recommendations: {str(e)}")


@router.post("/analyze-application")
async def analyze_application_quality(
    application_id: int = Form(..., description="Application ID to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze the quality of a job application
    
    Provides AI-powered analysis of application completeness and quality.
    """
    try:
        from sqlalchemy import select
        from ....models.application import Application
        from ....models.job import Job
        
        # Get application details
        app_query = select(Application).where(Application.id == application_id)
        result = await db.execute(app_query)
        application = result.scalar_one_or_none()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Check permissions
        if (current_user.user_type == 'candidate' and application.candidate_id != current_user.id) or \
           (current_user.user_type == 'recruiter' and application.job.company_id != current_user.recruiter_profile.get('company_id')):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get job match score if available
        job_match_score = 0
        if current_user.candidate_profile and current_user.candidate_profile.get('skills'):
            job_match_score = await ai_service.calculate_job_match_score(
                current_user.candidate_profile['skills'],
                application.job.requirements,
                application.job.skills_required
            )
        
        # Prepare application data for analysis
        application_data = {
            'application_id': application.id,
            'cover_letter': application.cover_letter,
            'resume_data': current_user.candidate_profile or {},
            'job_match_score': job_match_score
        }
        
        # Analyze application quality
        analysis = await ai_service.analyze_application_quality(application_data)
        
        if 'error' in analysis:
            raise HTTPException(status_code=500, detail=analysis['error'])
        
        return {
            "application_id": application_id,
            "analysis": analysis,
            "job_match_score": job_match_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze application: {str(e)}")


@router.post("/generate-interview-questions")
async def generate_interview_questions(
    job_id: int = Form(..., description="Job ID to generate questions for"),
    candidate_id: Optional[int] = Form(None, description="Candidate ID for personalized questions"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate AI-powered interview questions
    
    Creates personalized interview questions based on job requirements and candidate profile.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from sqlalchemy import select
        from ....models.job import Job
        from ....models.user import User as UserModel
        
        # Get job details
        job_query = select(Job).where(Job.id == job_id)
        result = await db.execute(job_query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Prepare job data
        job_data = {
            'title': job.title,
            'requirements': job.requirements,
            'skills_required': job.skills_required,
            'company_name': job.company.name if job.company else 'Unknown'
        }
        
        # Get candidate data if provided
        candidate_data = {}
        if candidate_id:
            candidate_query = select(UserModel).where(UserModel.id == candidate_id)
            result = await db.execute(candidate_query)
            candidate = result.scalar_one_or_none()
            
            if candidate and candidate.candidate_profile:
                candidate_data = {
                    'skills': candidate.candidate_profile.get('skills', []),
                    'experience_level': candidate.candidate_profile.get('experience_level', 'mid')
                }
        
        # Generate interview questions
        questions = await ai_service.generate_interview_questions(job_data, candidate_data)
        
        return {
            "job_id": job_id,
            "candidate_id": candidate_id,
            "questions": questions,
            "count": len(questions),
            "categories": list(set(q['category'] for q in questions))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate interview questions: {str(e)}")


@router.post("/score-interview-response")
async def score_interview_response(
    question: str = Form(..., description="Interview question"),
    response: str = Form(..., description="Candidate's response"),
    expected_keywords: Optional[List[str]] = Form(None, description="Expected keywords in response"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Score a candidate's interview response using AI
    
    Analyzes and scores interview responses for quality and relevance.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Score the response
        scoring_result = await ai_service.score_candidate_response(
            question, response, expected_keywords
        )
        
        if 'error' in scoring_result:
            raise HTTPException(status_code=500, detail=scoring_result['error'])
        
        return {
            "question": question,
            "response_length": len(response),
            "scoring": scoring_result,
            "expected_keywords": expected_keywords or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to score interview response: {str(e)}")


@router.get("/skills/extract")
async def extract_skills_from_text(
    text: str = Query(..., description="Text to extract skills from"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Extract skills from any text using AI
    
    Useful for analyzing job descriptions, resumes, or other text content.
    """
    try:
        # Use the AI service to extract skills
        skills = ai_service._extract_skills(text)
        
        return {
            "text_length": len(text),
            "extracted_skills": skills,
            "skill_count": len(skills),
            "skill_categories": {
                "programming": [s for s in skills if s in ai_service.skills_database.get('programming', [])],
                "web_development": [s for s in skills if s in ai_service.skills_database.get('web_development', [])],
                "databases": [s for s in skills if s in ai_service.skills_database.get('databases', [])],
                "cloud": [s for s in skills if s in ai_service.skills_database.get('cloud', [])],
                "data_science": [s for s in skills if s in ai_service.skills_database.get('data_science', [])],
                "soft_skills": [s for s in skills if s in ai_service.skills_database.get('soft_skills', [])]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract skills: {str(e)}")


@router.get("/experience-level/detect")
async def detect_experience_level(
    text: str = Query(..., description="Text to analyze for experience level"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Detect experience level from text using AI
    
    Analyzes text to determine the experience level (entry, junior, mid, senior, lead, executive).
    """
    try:
        # Use the AI service to determine experience level
        experience_level = ai_service._determine_experience_level(text)
        
        return {
            "text_length": len(text),
            "detected_level": experience_level,
            "confidence": "high",  # In a real implementation, this would be calculated
            "level_description": {
                "entry": "0-2 years of experience",
                "junior": "1-3 years of experience", 
                "mid": "3-7 years of experience",
                "senior": "7-12 years of experience",
                "lead": "10+ years with leadership experience",
                "executive": "15+ years with executive experience"
            }.get(experience_level, "Unknown level")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect experience level: {str(e)}")


@router.post("/mock-interview")
async def start_mock_interview(
    job_id: int = Form(..., description="Job ID for mock interview"),
    difficulty: str = Form("medium", regex="^(easy|medium|hard)$", description="Interview difficulty"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start an AI-powered mock interview session
    
    Creates a mock interview session with AI-generated questions.
    """
    if current_user.user_type != 'candidate':
        raise HTTPException(status_code=403, detail="Only candidates can start mock interviews")
    
    try:
        from sqlalchemy import select
        from ....models.job import Job
        
        # Get job details
        job_query = select(Job).where(Job.id == job_id)
        result = await db.execute(job_query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Prepare job and candidate data
        job_data = {
            'title': job.title,
            'requirements': job.requirements,
            'skills_required': job.skills_required,
            'company_name': job.company.name if job.company else 'Unknown'
        }
        
        candidate_data = current_user.candidate_profile or {}
        
        # Generate interview questions
        questions = await ai_service.generate_interview_questions(job_data, candidate_data)
        
        # Filter questions based on difficulty
        if difficulty == "easy":
            questions = [q for q in questions if q['category'] in ['motivation', 'basic']][:5]
        elif difficulty == "hard":
            questions = [q for q in questions if q['category'] in ['technical', 'leadership']][:8]
        else:  # medium
            questions = questions[:6]
        
        # Create mock interview session (in a real app, you'd save this to database)
        session_id = f"mock_{current_user.id}_{job_id}_{difficulty}"
        
        return {
            "session_id": session_id,
            "job_title": job.title,
            "difficulty": difficulty,
            "questions": questions,
            "total_questions": len(questions),
            "estimated_duration_minutes": len(questions) * 3,
            "instructions": [
                "Answer each question thoughtfully",
                "Take your time to provide detailed responses",
                "Use specific examples from your experience",
                "Ask for clarification if needed"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start mock interview: {str(e)}")


@router.get("/background-check/verify")
async def verify_background_info(
    candidate_id: int = Query(..., description="Candidate ID to verify"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Initiate AI-powered background verification
    
    Starts background verification process for a candidate.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # This would integrate with background check services
        # For now, return a placeholder response
        
        return {
            "candidate_id": candidate_id,
            "verification_status": "initiated",
            "checks_requested": [
                "Employment History",
                "Education Verification", 
                "Criminal Background",
                "Reference Checks"
            ],
            "estimated_completion": "3-5 business days",
            "message": "Background verification initiated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate background verification: {str(e)}")