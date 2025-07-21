"""
Analytics API Endpoints

Analytics and reporting endpoints for recruitment metrics.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....services.analytics_service import analytics_service

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard analytics based on user type
    
    Returns different analytics based on whether the user is a candidate, recruiter, or admin.
    """
    try:
        stats = await analytics_service.get_dashboard_stats(
            db, current_user.id, current_user.user_type
        )
        
        return {
            "user_type": current_user.user_type,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard analytics: {str(e)}")


@router.get("/jobs/{job_id}")
async def get_job_analytics(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed analytics for a specific job
    
    Only accessible by recruiters and admins.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        analytics = await analytics_service.get_job_analytics(db, job_id)
        
        if 'error' in analytics:
            raise HTTPException(status_code=404, detail=analytics['error'])
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job analytics: {str(e)}")


@router.get("/applications")
async def get_application_analytics(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get application analytics
    
    For recruiters: shows analytics for their company
    For admins: shows platform-wide analytics or specific company if company_id provided
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # For recruiters, use their company ID
        if current_user.user_type == 'recruiter':
            if current_user.recruiter_profile:
                company_id = current_user.recruiter_profile.get('company_id')
            else:
                raise HTTPException(status_code=400, detail="Recruiter profile not found")
        
        analytics = await analytics_service.get_application_analytics(db, company_id)
        
        if 'error' in analytics:
            raise HTTPException(status_code=500, detail=analytics['error'])
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application analytics: {str(e)}")


@router.get("/trends/applications")
async def get_application_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get application trends over time
    
    Returns application trends for the specified time period.
    """
    try:
        # This would be implemented in the analytics service
        # For now, return a placeholder
        return {
            "period_days": days,
            "trends": [],
            "message": "Application trends analysis coming soon"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application trends: {str(e)}")


@router.get("/performance/jobs")
async def get_job_performance(
    limit: int = Query(10, ge=1, le=50, description="Number of top jobs to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get top performing jobs by application count
    
    Only accessible by recruiters and admins.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get company ID for recruiters
        company_id = None
        if current_user.user_type == 'recruiter':
            if current_user.recruiter_profile:
                company_id = current_user.recruiter_profile.get('company_id')
            else:
                raise HTTPException(status_code=400, detail="Recruiter profile not found")
        
        # This would be implemented in the analytics service
        return {
            "top_jobs": [],
            "limit": limit,
            "company_id": company_id,
            "message": "Job performance analysis coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job performance: {str(e)}")


@router.get("/conversion-rates")
async def get_conversion_rates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get conversion rates for the recruitment funnel
    
    Shows conversion rates from application to hire.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get company ID for recruiters
        company_id = None
        if current_user.user_type == 'recruiter':
            if current_user.recruiter_profile:
                company_id = current_user.recruiter_profile.get('company_id')
        
        # This would be implemented in the analytics service
        return {
            "conversion_rates": {
                "application_to_review": 0.0,
                "review_to_interview": 0.0,
                "interview_to_offer": 0.0,
                "offer_to_hire": 0.0
            },
            "company_id": company_id,
            "message": "Conversion rate analysis coming soon"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversion rates: {str(e)}")


@router.get("/time-to-hire")
async def get_time_to_hire_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get time-to-hire metrics
    
    Shows average time from application to hire.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get company ID for recruiters
        company_id = None
        if current_user.user_type == 'recruiter':
            if current_user.recruiter_profile:
                company_id = current_user.recruiter_profile.get('company_id')
        
        # This would be implemented in the analytics service
        return {
            "average_time_to_hire_days": 0.0,
            "median_time_to_hire_days": 0.0,
            "time_by_position": [],
            "company_id": company_id,
            "message": "Time-to-hire analysis coming soon"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get time-to-hire metrics: {str(e)}")


@router.get("/candidate-sources")
async def get_candidate_sources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get candidate source analytics
    
    Shows where candidates are coming from (direct, referrals, job boards, etc.).
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # This would track candidate sources and provide analytics
        return {
            "sources": [
                {"source": "Direct Application", "count": 0, "percentage": 0.0},
                {"source": "Job Boards", "count": 0, "percentage": 0.0},
                {"source": "Referrals", "count": 0, "percentage": 0.0},
                {"source": "Social Media", "count": 0, "percentage": 0.0}
            ],
            "message": "Candidate source analysis coming soon"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get candidate sources: {str(e)}")


@router.get("/skills-demand")
async def get_skills_demand_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get skills demand analytics
    
    Shows which skills are most in demand based on job postings and applications.
    """
    try:
        # This would analyze job requirements and candidate skills
        return {
            "top_skills": [
                {"skill": "Python", "demand_score": 0, "jobs_requiring": 0},
                {"skill": "JavaScript", "demand_score": 0, "jobs_requiring": 0},
                {"skill": "React", "demand_score": 0, "jobs_requiring": 0},
                {"skill": "SQL", "demand_score": 0, "jobs_requiring": 0}
            ],
            "trending_skills": [],
            "message": "Skills demand analysis coming soon"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get skills demand analytics: {str(e)}")


@router.post("/reports/generate")
async def generate_analytics_report(
    report_type: str = Query(..., regex="^(monthly|quarterly|annual|custom)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a comprehensive analytics report
    
    Generates and queues a detailed analytics report for download.
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from ....utils.background_tasks import task_manager, generate_analytics_report_task
        
        # Get company ID for recruiters
        company_id = None
        if current_user.user_type == 'recruiter':
            if current_user.recruiter_profile:
                company_id = current_user.recruiter_profile.get('company_id')
        
        # Schedule report generation
        task_id = await task_manager.add_task(
            generate_analytics_report_task,
            company_id=company_id,
            report_type=report_type
        )
        
        return {
            "message": "Report generation started",
            "task_id": task_id,
            "report_type": report_type,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/reports/{task_id}/status")
async def get_report_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the status of a report generation task
    """
    if current_user.user_type not in ['recruiter', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        from ....utils.background_tasks import task_manager
        
        task_status = task_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task_id,
            "status": task_status['status'],
            "created_at": task_status['created_at'].isoformat() if task_status['created_at'] else None,
            "completed_at": task_status.get('completed_at').isoformat() if task_status.get('completed_at') else None,
            "result": task_status.get('result'),
            "error": task_status.get('error')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report status: {str(e)}")