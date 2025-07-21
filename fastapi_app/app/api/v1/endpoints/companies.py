"""
Company Management Endpoints

Handles company information and company-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_recruiter
from app.core.exceptions import NotFoundException, ValidationException
from app.models.company import Company
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_companies(
    skip: int = Query(0, ge=0, description="Number of companies to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of companies to return"),
    search: Optional[str] = Query(None, description="Search term for company name"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    company_size: Optional[str] = Query(None, description="Company size filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    List companies with filtering and pagination
    
    Returns a paginated list of active companies with optional filtering.
    """
    query = select(Company).where(Company.is_active == True)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(Company.name.ilike(search_term))
    
    if industry:
        query = query.where(Company.industry == industry)
    
    if company_size:
        query = query.where(Company.company_size == company_size)
    
    # Apply pagination and ordering
    query = query.order_by(Company.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    # Get total count for pagination
    count_query = select(func.count(Company.id)).where(Company.is_active == True)
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(Company.name.ilike(search_term))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return {
        "companies": companies,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }


@router.get("/{company_id}")
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get company details by ID
    
    Returns detailed company information.
    """
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise NotFoundException("Company not found")
    
    if not company.is_active:
        raise NotFoundException("Company not found")
    
    return company


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: dict,  # Simplified for now
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new company
    
    Creates a new company (admin or authorized recruiters only).
    """
    # Check if company name already exists
    result = await db.execute(
        select(Company).where(Company.name == company_data.get("name"))
    )
    existing_company = result.scalar_one_or_none()
    
    if existing_company:
        raise ValidationException("Company with this name already exists")
    
    # Create company slug
    from slugify import slugify
    slug = slugify(company_data.get("name"))
    
    # Check if slug already exists
    slug_result = await db.execute(
        select(Company).where(Company.slug == slug)
    )
    existing_slug = slug_result.scalar_one_or_none()
    
    if existing_slug:
        # Add a number to make it unique
        counter = 1
        while existing_slug:
            new_slug = f"{slug}-{counter}"
            slug_result = await db.execute(
                select(Company).where(Company.slug == new_slug)
            )
            existing_slug = slug_result.scalar_one_or_none()
            if not existing_slug:
                slug = new_slug
                break
            counter += 1
    
    # Create company
    company = Company(
        name=company_data.get("name"),
        slug=slug,
        description=company_data.get("description"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        website=company_data.get("website"),
        location=company_data.get("location"),
        is_active=True,
        is_verified=False
    )
    
    db.add(company)
    await db.commit()
    await db.refresh(company)
    
    # Associate recruiter with company
    if current_user.recruiter_profile:
        current_user.recruiter_profile.company_id = company.id
        await db.commit()
    
    return company


@router.put("/{company_id}")
async def update_company(
    company_id: int,
    company_data: dict,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
):
    """
    Update company information
    
    Updates company information (authorized recruiters only).
    """
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise NotFoundException("Company not found")
    
    # Check if user has permission to update this company
    if (current_user.recruiter_profile.company_id != company_id and 
        not current_user.is_superuser):
        raise ValidationException("You don't have permission to update this company")
    
    # Update company fields (simplified)
    update_fields = [
        "description", "industry", "company_size", "website", 
        "location", "tagline", "mission", "vision"
    ]
    
    for field in update_fields:
        if field in company_data:
            setattr(company, field, company_data[field])
    
    await db.commit()
    await db.refresh(company)
    
    return company


@router.get("/{company_id}/jobs")
async def get_company_jobs(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get jobs for a specific company
    
    Returns active jobs posted by the company.
    """
    # Verify company exists
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company or not company.is_active:
        raise NotFoundException("Company not found")
    
    # Get jobs
    from app.models.job import Job
    
    jobs_query = select(Job).where(
        Job.company_id == company_id,
        Job.status == "active"
    ).order_by(Job.created_at.desc()).offset(skip).limit(limit)
    
    jobs_result = await db.execute(jobs_query)
    jobs = jobs_result.scalars().all()
    
    return {
        "company": company,
        "jobs": jobs,
        "skip": skip,
        "limit": limit
    }