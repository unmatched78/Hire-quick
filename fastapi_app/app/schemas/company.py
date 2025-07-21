"""
Company Pydantic Schemas

Request and response models for company-related API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CompanySize(str, Enum):
    """Company size enumeration"""
    STARTUP = "startup"  # 1-10
    SMALL = "small"      # 11-50
    MEDIUM = "medium"    # 51-200
    LARGE = "large"      # 201-1000
    ENTERPRISE = "enterprise"  # 1000+


class Industry(str, Enum):
    """Industry enumeration"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    MEDIA = "media"
    REAL_ESTATE = "real_estate"
    AUTOMOTIVE = "automotive"
    ENERGY = "energy"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    OTHER = "other"


# Base schemas
class CompanyBase(BaseModel):
    """Base company schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    industry: Optional[Industry] = None
    company_size: Optional[CompanySize] = None
    website: Optional[HttpUrl] = None
    location: Optional[str] = Field(None, max_length=200)
    founded_year: Optional[int] = Field(None, ge=1800, le=2024)
    
    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v > current_year:
                raise ValueError('Founded year cannot be in the future')
        return v


class CompanyCreate(CompanyBase):
    """Company creation schema"""
    pass


class CompanyUpdate(BaseModel):
    """Company update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    industry: Optional[Industry] = None
    company_size: Optional[CompanySize] = None
    website: Optional[HttpUrl] = None
    location: Optional[str] = Field(None, max_length=200)
    founded_year: Optional[int] = Field(None, ge=1800, le=2024)
    is_verified: Optional[bool] = None
    
    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v > current_year:
                raise ValueError('Founded year cannot be in the future')
        return v


class CompanyResponse(CompanyBase):
    """Company response schema"""
    id: int
    is_verified: bool = False
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Statistics
    total_jobs: int = 0
    active_jobs: int = 0
    total_employees: int = 0
    
    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Company list response schema"""
    companies: List[CompanyResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CompanyFilters(BaseModel):
    """Company filters schema"""
    search: Optional[str] = Field(None, description="Search in company name and description")
    industry: Optional[List[Industry]] = Field(None, description="Filter by industries")
    company_size: Optional[List[CompanySize]] = Field(None, description="Filter by company size")
    location: Optional[str] = Field(None, description="Filter by location")
    is_verified: Optional[bool] = Field(None, description="Filter by verification status")
    has_active_jobs: Optional[bool] = Field(None, description="Filter companies with active jobs")


class CompanyStats(BaseModel):
    """Company statistics schema"""
    company_id: int
    total_jobs_posted: int
    active_jobs: int
    total_applications: int
    total_hires: int
    average_time_to_hire: Optional[float] = None  # in days
    top_job_categories: List[dict]
    application_conversion_rate: float
    jobs_by_status: dict
    applications_by_month: List[dict]


class CompanyTeamMember(BaseModel):
    """Company team member schema"""
    id: int
    user_id: int
    company_id: int
    role: str = Field(..., regex="^(admin|recruiter|hr_manager|viewer)$")
    permissions: List[str] = Field(default_factory=list)
    joined_at: datetime
    is_active: bool = True
    
    # User details
    name: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class CompanyTeamInvite(BaseModel):
    """Company team invite schema"""
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    role: str = Field(..., regex="^(admin|recruiter|hr_manager|viewer)$")
    permissions: Optional[List[str]] = Field(default_factory=list)
    message: Optional[str] = Field(None, max_length=500)


class CompanyBranding(BaseModel):
    """Company branding schema"""
    primary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    custom_css: Optional[str] = Field(None, max_length=5000)
    social_links: Optional[dict] = Field(default_factory=dict)


class CompanyWithJobs(CompanyResponse):
    """Company response with jobs"""
    recent_jobs: List[dict] = Field(default_factory=list)
    job_categories: List[dict] = Field(default_factory=list)