"""
Job Models

SQLAlchemy models for job management including:
- Job (job postings)
- ApplicationFormField (custom application form fields)
- SavedJob (saved jobs by candidates)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class JobType(str, enum.Enum):
    """Job type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    EXPIRED = "expired"


class ExperienceLevel(str, enum.Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class RemoteType(str, enum.Enum):
    """Remote work type enumeration"""
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class Job(Base):
    """
    Job posting model
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    recruiter_id = Column(Integer, ForeignKey("recruiter_profiles.id"), nullable=False)
    
    # Basic job information
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # Short summary for listings
    
    # Job details
    job_type = Column(String(20), default=JobType.FULL_TIME)
    experience_level = Column(String(20), default=ExperienceLevel.MID)
    remote_type = Column(String(20), default=RemoteType.ONSITE)
    
    # Location
    location = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    is_remote_ok = Column(Boolean, default=False)
    
    # Requirements and qualifications
    requirements = Column(JSON, default=list)  # Required skills/qualifications
    preferred_qualifications = Column(JSON, default=list)  # Preferred skills
    education_requirements = Column(JSON, default=list)  # Education requirements
    
    # Experience requirements
    min_experience_years = Column(Integer, default=0)
    max_experience_years = Column(Integer, nullable=True)
    
    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(3), default="USD")
    salary_type = Column(String(20), default="annual")  # annual, hourly, project
    equity_offered = Column(Boolean, default=False)
    
    # Benefits and perks
    benefits = Column(JSON, default=list)
    perks = Column(JSON, default=list)
    
    # Application settings
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    max_applications = Column(Integer, nullable=True)
    auto_reject_after_deadline = Column(Boolean, default=False)
    
    # Custom application form
    has_custom_form = Column(Boolean, default=False)
    require_cover_letter = Column(Boolean, default=False)
    require_resume = Column(Boolean, default=True)
    
    # Job status and visibility
    status = Column(String(20), default=JobStatus.DRAFT)
    is_featured = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    
    # SEO and discoverability
    keywords = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    category = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    application_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    recruiter = relationship("RecruiterProfile", back_populates="posted_jobs")
    applications = relationship("Application", back_populates="job")
    saved_by = relationship("SavedJob", back_populates="job")
    form_fields = relationship("ApplicationFormField", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def salary_range(self):
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        return None
    
    @property
    def is_expired(self):
        """Check if job is expired"""
        if self.expires_at:
            return func.now() > self.expires_at
        return False


class ApplicationFormField(Base):
    """
    Custom application form fields for jobs
    """
    __tablename__ = "application_form_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Field configuration
    field_type = Column(String(50), nullable=False)  # text, textarea, select, etc.
    label = Column(String(200), nullable=False)
    placeholder = Column(String(200), nullable=True)
    help_text = Column(Text, nullable=True)
    
    # Field validation
    is_required = Column(Boolean, default=True)
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    
    # Field options (for select, radio, checkbox)
    options = Column(JSON, default=list)
    
    # File upload settings
    allowed_file_types = Column(JSON, default=list)
    max_file_size_mb = Column(Integer, default=10)
    
    # Field ordering
    order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="form_fields")
    
    def __repr__(self):
        return f"<ApplicationFormField(id={self.id}, job_id={self.job_id}, label='{self.label}')>"


class SavedJob(Base):
    """
    Jobs saved by candidates
    """
    __tablename__ = "saved_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Save metadata
    notes = Column(Text, nullable=True)  # Private notes from candidate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")
    
    def __repr__(self):
        return f"<SavedJob(candidate_id={self.candidate_id}, job_id={self.job_id})>"


class JobView(Base):
    """
    Track job views for analytics
    """
    __tablename__ = "job_views"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous views
    
    # View metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Timestamps
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job")
    user = relationship("User")
    
    def __repr__(self):
        return f"<JobView(job_id={self.job_id}, user_id={self.user_id})>"


class JobAlert(Base):
    """
    Job alerts for candidates
    """
    __tablename__ = "job_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert configuration
    name = Column(String(200), nullable=False)
    keywords = Column(JSON, default=list)
    locations = Column(JSON, default=list)
    job_types = Column(JSON, default=list)
    experience_levels = Column(JSON, default=list)
    remote_types = Column(JSON, default=list)
    
    # Salary filters
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    
    # Alert settings
    is_active = Column(Boolean, default=True)
    frequency = Column(String(20), default="daily")  # immediate, daily, weekly
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<JobAlert(id={self.id}, user_id={self.user_id}, name='{self.name}')>"