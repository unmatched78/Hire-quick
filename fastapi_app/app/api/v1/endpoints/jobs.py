"""
Job Management Endpoints

Handles job posting, searching, and management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_recruiter
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
from app.models.job import Job, SavedJob
from app.models.user import User

router = APIRouter()


@router.get("", include_in_schema=True)
@router.get("/", include_in_schema=False)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of jobs to return"),
    search: Optional[str] = Query(None, description="Search term for job title or description"),
    location: Optional[str] = Query(None, description="Job location filter"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    remote_ok: Optional[bool] = Query(None, description="Remote work filter"),
    min_salary: Optional[int] = Query(None, description="Minimum salary filter"),
    max_salary: Optional[int] = Query(None, description="Maximum salary filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    List jobs with filtering and pagination
    
    Returns a paginated list of active jobs with optional filtering.
    """
    query = select(Job).where(Job.status == "active")
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Job.title.ilike(search_term),
                Job.description.ilike(search_term),
                Job.summary.ilike(search_term)
            )
        )
    
    if location:
        location_term = f"%{location}%"
        query = query.where(Job.location.ilike(location_term))
    
    if job_type:
        query = query.where(Job.job_type == job_type)
    
    if remote_ok is not None:
        query = query.where(Job.is_remote_ok == remote_ok)
    
    if min_salary:
        query = query.where(Job.salary_min >= min_salary)
    
    if max_salary:
        query = query.where(Job.salary_max <= max_salary)
    
    # Apply pagination and ordering
    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    # Get total count for pagination
    count_query = select(func.count(Job.id)).where(Job.status == "active")
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            or_(
                Job.title.ilike(search_term),
                Job.description.ilike(search_term),
                Job.summary.ilike(search_term)
            )
        )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return {
        "jobs": jobs,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get job details by ID
    
    Returns detailed job information. Increments view count.
    """
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise NotFoundException("Job not found")
    
    # Increment view count
    job.view_count += 1
    await db.commit()
    
    # Check if job is saved by current user (if authenticated)
    is_saved = False
    if current_user and current_user.user_type == "candidate":
        saved_result = await db.execute(
            select(SavedJob).where(
                and_(
                    SavedJob.job_id == job_id,
                    SavedJob.candidate_id == current_user.candidate_profile.id
                )
            )
        )
        is_saved = saved_result.scalar_one_or_none() is not None
    
    job_data = {
        **job.__dict__,
        "is_saved": is_saved
    }
    
    return job_data


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: dict,  # Simplified for now
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job posting
    
    Creates a new job posting for the current recruiter.
    """
    # Get recruiter profile
    if not current_user.recruiter_profile:
        raise ValidationException("Recruiter profile not found")
    
    if not current_user.recruiter_profile.can_post_jobs:
        raise AuthorizationException("You don't have permission to post jobs")
    
    # Create job (simplified implementation)
    job = Job(
        title=job_data.get("title"),
        description=job_data.get("description"),
        company_id=current_user.recruiter_profile.company_id,
        recruiter_id=current_user.recruiter_profile.id,
        location=job_data.get("location"),
        job_type=job_data.get("job_type", "full_time"),
        remote_type=job_data.get("remote_type", "onsite"),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        requirements=job_data.get("requirements", []),
        status="draft"
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return job


@router.post("/{job_id}/save")
async def save_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save a job for later
    
    Adds the job to the candidate's saved jobs list.
    """
    if current_user.user_type != "candidate":
        raise AuthorizationException("Only candidates can save jobs")
    
    # Check if job exists
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise NotFoundException("Job not found")
    
    # Check if already saved
    saved_result = await db.execute(
        select(SavedJob).where(
            and_(
                SavedJob.job_id == job_id,
                SavedJob.candidate_id == current_user.candidate_profile.id
            )
        )
    )
    existing_save = saved_result.scalar_one_or_none()
    
    if existing_save:
        return {"message": "Job already saved"}
    
    # Save job
    saved_job = SavedJob(
        job_id=job_id,
        candidate_id=current_user.candidate_profile.id
    )
    
    db.add(saved_job)
    await db.commit()
    
    return {"message": "Job saved successfully"}


@router.delete("/{job_id}/save")
async def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a job from saved jobs
    
    Removes the job from the candidate's saved jobs list.
    """
    if current_user.user_type != "candidate":
        raise AuthorizationException("Only candidates can unsave jobs")
    
    # Find and remove saved job
    result = await db.execute(
        select(SavedJob).where(
            and_(
                SavedJob.job_id == job_id,
                SavedJob.candidate_id == current_user.candidate_profile.id
            )
        )
    )
    saved_job = result.scalar_one_or_none()
    
    if not saved_job:
        raise NotFoundException("Saved job not found")
    
    await db.delete(saved_job)
    await db.commit()
    
    return {"message": "Job removed from saved jobs"}