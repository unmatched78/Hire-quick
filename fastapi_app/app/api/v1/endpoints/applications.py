"""
Application Management Endpoints

Handles job applications, application tracking, and related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_candidate, require_recruiter
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
from app.models.application import Application
from app.models.job import Job
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_applications(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of applications to return"),
    status_filter: Optional[str] = Query(None, description="Filter by application status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List applications
    
    Returns applications based on user type:
    - Candidates see their own applications
    - Recruiters see applications for their jobs
    """
    if current_user.user_type == "candidate":
        # Candidate sees their own applications
        query = select(Application).where(
            Application.candidate_id == current_user.candidate_profile.id
        )
    
    elif current_user.user_type == "recruiter":
        # Recruiter sees applications for their jobs
        query = select(Application).join(Job).where(
            Job.recruiter_id == current_user.recruiter_profile.id
        )
    
    else:
        raise AuthorizationException("Access denied")
    
    # Apply status filter
    if status_filter:
        query = query.where(Application.status == status_filter)
    
    # Apply pagination and ordering
    query = query.order_by(Application.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return {
        "applications": applications,
        "skip": skip,
        "limit": limit
    }


@router.get("/{application_id}")
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get application details by ID
    
    Returns detailed application information if user has access.
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise NotFoundException("Application not found")
    
    # Check access permissions
    has_access = False
    
    if current_user.user_type == "candidate":
        # Candidate can only see their own applications
        has_access = application.candidate_id == current_user.candidate_profile.id
    
    elif current_user.user_type == "recruiter":
        # Recruiter can see applications for their jobs
        job_result = await db.execute(
            select(Job).where(Job.id == application.job_id)
        )
        job = job_result.scalar_one_or_none()
        has_access = job and job.recruiter_id == current_user.recruiter_profile.id
    
    if not has_access:
        raise AuthorizationException("Access denied")
    
    # Mark as viewed by recruiter
    if current_user.user_type == "recruiter" and not application.viewed_by_recruiter:
        from datetime import datetime
        application.viewed_by_recruiter = True
        application.viewed_at = datetime.utcnow()
        await db.commit()
    
    return application


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: dict,  # Simplified for now
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job application
    
    Submits an application for a job.
    """
    job_id = application_data.get("job_id")
    
    if not job_id:
        raise ValidationException("Job ID is required")
    
    # Check if job exists and is active
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise NotFoundException("Job not found")
    
    if job.status != "active":
        raise ValidationException("Job is not accepting applications")
    
    # Check if user already applied
    existing_result = await db.execute(
        select(Application).where(
            and_(
                Application.job_id == job_id,
                Application.candidate_id == current_user.candidate_profile.id
            )
        )
    )
    existing_application = existing_result.scalar_one_or_none()
    
    if existing_application:
        raise ValidationException("You have already applied for this job")
    
    # Create application
    from datetime import datetime
    
    application = Application(
        job_id=job_id,
        candidate_id=current_user.candidate_profile.id,
        cover_letter=application_data.get("cover_letter"),
        form_responses=application_data.get("form_responses", {}),
        status="submitted",
        submitted_at=datetime.utcnow()
    )
    
    db.add(application)
    
    # Update job application count
    job.application_count += 1
    
    await db.commit()
    await db.refresh(application)
    
    return application


@router.put("/{application_id}/status")
async def update_application_status(
    application_id: int,
    status_data: dict,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
):
    """
    Update application status
    
    Updates the status of an application (recruiter only).
    """
    new_status = status_data.get("status")
    notes = status_data.get("notes")
    
    if not new_status:
        raise ValidationException("Status is required")
    
    # Get application
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise NotFoundException("Application not found")
    
    # Check if recruiter owns the job
    job_result = await db.execute(
        select(Job).where(Job.id == application.job_id)
    )
    job = job_result.scalar_one_or_none()
    
    if not job or job.recruiter_id != current_user.recruiter_profile.id:
        raise AuthorizationException("Access denied")
    
    # Update application
    application.status = new_status
    if notes:
        application.recruiter_notes = notes
    
    await db.commit()
    await db.refresh(application)
    
    return application


@router.delete("/{application_id}")
async def withdraw_application(
    application_id: int,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraw application
    
    Allows candidate to withdraw their application.
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise NotFoundException("Application not found")
    
    # Check if candidate owns the application
    if application.candidate_id != current_user.candidate_profile.id:
        raise AuthorizationException("Access denied")
    
    # Check if application can be withdrawn
    if application.status in ["hired", "offer_accepted"]:
        raise ValidationException("Cannot withdraw application in current status")
    
    # Update status to withdrawn
    application.status = "withdrawn"
    await db.commit()
    
    return {"message": "Application withdrawn successfully"}