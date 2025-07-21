"""
Job Pydantic Schemas

Request and response models for job-related API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    """Job type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class JobStatus(str, Enum):
    """Job status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    CLOSED = "closed"


class ExperienceLevel(str, Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class WorkLocation(str, Enum):
    """Work location enumeration"""
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


# Base schemas
class JobBase(BaseModel):
    """Base job schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    requirements: str = Field(..., min_length=10)
    job_type: JobType = JobType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID
    work_location: WorkLocation = WorkLocation.ONSITE
    location: Optional[str] = Field(None, max_length=200)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = Field("USD", max_length=3)
    benefits: Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)
    application_deadline: Optional[datetime] = None
    
    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        if v is not None and 'salary_min' in values and values['salary_min'] is not None:
            if v < values['salary_min']:
                raise ValueError('Maximum salary must be greater than minimum salary')
        return v


class JobCreate(JobBase):
    """Job creation schema"""
    custom_application_fields: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class JobUpdate(BaseModel):
    """Job update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    requirements: Optional[str] = Field(None, min_length=10)
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    work_location: Optional[WorkLocation] = None
    location: Optional[str] = Field(None, max_length=200)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    benefits: Optional[str] = None
    skills_required: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    status: Optional[JobStatus] = None
    custom_application_fields: Optional[List[Dict[str, Any]]] = None


class JobResponse(JobBase):
    """Job response schema"""
    id: int
    company_id: int
    recruiter_id: int
    status: JobStatus
    views_count: int = 0
    applications_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime]
    is_saved: Optional[bool] = False  # For authenticated users
    
    # Related data
    company_name: Optional[str] = None
    recruiter_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response schema"""
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    pages: int


class JobSearchFilters(BaseModel):
    """Job search and filter schema"""
    search: Optional[str] = Field(None, description="Search in title and description")
    job_type: Optional[List[JobType]] = Field(None, description="Filter by job types")
    experience_level: Optional[List[ExperienceLevel]] = Field(None, description="Filter by experience levels")
    work_location: Optional[List[WorkLocation]] = Field(None, description="Filter by work location")
    location: Optional[str] = Field(None, description="Filter by location")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary filter")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary filter")
    skills: Optional[List[str]] = Field(None, description="Filter by required skills")
    company_id: Optional[int] = Field(None, description="Filter by company")
    posted_since: Optional[int] = Field(None, ge=1, le=365, description="Posted within X days")


class SavedJobResponse(BaseModel):
    """Saved job response schema"""
    id: int
    job_id: int
    user_id: int
    saved_at: datetime
    job: JobResponse
    
    class Config:
        from_attributes = True


class JobAnalytics(BaseModel):
    """Job analytics schema"""
    job_id: int
    views_count: int
    applications_count: int
    applications_by_status: Dict[str, int]
    views_by_date: List[Dict[str, Any]]
    applications_by_date: List[Dict[str, Any]]
    top_skills_applied: List[Dict[str, Any]]
    average_application_score: Optional[float] = None