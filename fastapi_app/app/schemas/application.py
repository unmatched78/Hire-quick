"""
Application Pydantic Schemas

Request and response models for application-related API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_EXTENDED = "offer_extended"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class InterviewType(str, Enum):
    """Interview type enumeration"""
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    FINAL = "final"


# Base schemas
class ApplicationBase(BaseModel):
    """Base application schema"""
    cover_letter: Optional[str] = Field(None, max_length=2000)
    custom_responses: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ApplicationCreate(ApplicationBase):
    """Application creation schema"""
    job_id: int = Field(..., gt=0)


class ApplicationUpdate(BaseModel):
    """Application update schema"""
    cover_letter: Optional[str] = Field(None, max_length=2000)
    custom_responses: Optional[Dict[str, Any]] = None


class ApplicationStatusUpdate(BaseModel):
    """Application status update schema"""
    status: ApplicationStatus
    notes: Optional[str] = Field(None, max_length=1000)
    interview_scheduled_at: Optional[datetime] = None
    interview_type: Optional[InterviewType] = None
    interview_location: Optional[str] = Field(None, max_length=500)
    interview_notes: Optional[str] = Field(None, max_length=1000)


class ApplicationResponse(ApplicationBase):
    """Application response schema"""
    id: int
    job_id: int
    candidate_id: int
    status: ApplicationStatus
    applied_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    
    # Files
    resume_url: Optional[str] = None
    portfolio_urls: Optional[List[str]] = Field(default_factory=list)
    
    # Interview details
    interview_scheduled_at: Optional[datetime] = None
    interview_type: Optional[InterviewType] = None
    interview_location: Optional[str] = None
    interview_notes: Optional[str] = None
    
    # Scoring and notes
    recruiter_notes: Optional[str] = None
    application_score: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    """Application list response schema"""
    applications: List[ApplicationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ApplicationFilters(BaseModel):
    """Application filters schema"""
    status: Optional[List[ApplicationStatus]] = Field(None, description="Filter by status")
    job_id: Optional[int] = Field(None, description="Filter by job")
    company_id: Optional[int] = Field(None, description="Filter by company")
    applied_since: Optional[int] = Field(None, ge=1, le=365, description="Applied within X days")
    interview_scheduled: Optional[bool] = Field(None, description="Filter by interview scheduled")
    score_min: Optional[float] = Field(None, ge=0, le=100, description="Minimum application score")
    score_max: Optional[float] = Field(None, ge=0, le=100, description="Maximum application score")


class InterviewSchedule(BaseModel):
    """Interview schedule schema"""
    application_id: int
    interview_type: InterviewType
    scheduled_at: datetime
    location: Optional[str] = Field(None, max_length=500)
    duration_minutes: int = Field(60, ge=15, le=480)
    interviewer_notes: Optional[str] = Field(None, max_length=1000)
    meeting_link: Optional[str] = Field(None, max_length=500)


class InterviewResponse(BaseModel):
    """Interview response schema"""
    id: int
    application_id: int
    interview_type: InterviewType
    scheduled_at: datetime
    location: Optional[str] = None
    duration_minutes: int
    interviewer_notes: Optional[str] = None
    meeting_link: Optional[str] = None
    status: str = "scheduled"  # scheduled, completed, cancelled, no_show
    feedback: Optional[str] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    created_at: datetime
    
    # Related data
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    
    class Config:
        from_attributes = True


class ApplicationAnalytics(BaseModel):
    """Application analytics schema"""
    total_applications: int
    applications_by_status: Dict[str, int]
    applications_by_job: List[Dict[str, Any]]
    applications_by_date: List[Dict[str, Any]]
    average_time_to_hire: Optional[float] = None  # in days
    conversion_rates: Dict[str, float]
    top_rejection_reasons: List[Dict[str, Any]]


class BulkApplicationAction(BaseModel):
    """Bulk application action schema"""
    application_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., regex="^(reject|shortlist|schedule_interview)$")
    notes: Optional[str] = Field(None, max_length=1000)
    interview_details: Optional[InterviewSchedule] = None