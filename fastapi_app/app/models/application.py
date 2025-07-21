"""
Application Models

SQLAlchemy models for application management including:
- Application (job applications)
- ApplicationFile (uploaded files)
- ParsedResume (AI-parsed resume data)
- Interview (interview scheduling)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_EXTENDED = "offer_extended"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class InterviewType(str, enum.Enum):
    """Interview type enumeration"""
    PHONE = "phone"
    VIDEO = "video"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    FINAL = "final"
    PANEL = "panel"


class InterviewStatus(str, enum.Enum):
    """Interview status enumeration"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class Application(Base):
    """
    Job application model
    """
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    
    # Application status
    status = Column(String(30), default=ApplicationStatus.SUBMITTED)
    
    # Traditional application fields
    cover_letter = Column(Text, nullable=True)
    resume_file = Column(String(500), nullable=True)
    
    # Dynamic form responses (JSON field for custom form data)
    form_responses = Column(JSON, default=dict)
    
    # Application metadata
    source = Column(String(100), nullable=True)  # website, linkedin, referral, etc.
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Recruiter notes and feedback
    recruiter_notes = Column(Text, nullable=True)
    internal_rating = Column(Float, nullable=True)  # 1-5 scale
    
    # Application tracking
    viewed_by_recruiter = Column(Boolean, default=False)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("CandidateProfile", back_populates="applications")
    referrer = relationship("User", foreign_keys=[referrer_id])
    uploaded_files = relationship("ApplicationFile", back_populates="application", cascade="all, delete-orphan")
    parsed_resume = relationship("ParsedResume", back_populates="application", uselist=False)
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, status='{self.status}')>"
    
    @property
    def status_display(self):
        """Get human-readable status"""
        status_map = {
            ApplicationStatus.DRAFT: "Draft",
            ApplicationStatus.SUBMITTED: "Submitted",
            ApplicationStatus.UNDER_REVIEW: "Under Review",
            ApplicationStatus.SCREENING: "Screening",
            ApplicationStatus.INTERVIEW_SCHEDULED: "Interview Scheduled",
            ApplicationStatus.INTERVIEWED: "Interviewed",
            ApplicationStatus.OFFER_EXTENDED: "Offer Extended",
            ApplicationStatus.OFFER_ACCEPTED: "Offer Accepted",
            ApplicationStatus.OFFER_DECLINED: "Offer Declined",
            ApplicationStatus.HIRED: "Hired",
            ApplicationStatus.REJECTED: "Rejected",
            ApplicationStatus.WITHDRAWN: "Withdrawn"
        }
        return status_map.get(self.status, self.status.title())


class ApplicationFile(Base):
    """
    Files uploaded with applications
    """
    __tablename__ = "application_files"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    form_field_id = Column(Integer, ForeignKey("application_form_fields.id"), nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    content_type = Column(String(100), nullable=False)
    file_type = Column(String(50), nullable=True)  # resume, cover_letter, portfolio, etc.
    
    # File processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    application = relationship("Application", back_populates="uploaded_files")
    form_field = relationship("ApplicationFormField")
    
    def __repr__(self):
        return f"<ApplicationFile(id={self.id}, filename='{self.original_filename}')>"
    
    @property
    def file_size_display(self):
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class ParsedResume(Base):
    """
    AI-parsed resume data
    """
    __tablename__ = "parsed_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False)
    
    # Contact information
    full_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Professional summary
    summary = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    
    # Skills (categorized)
    technical_skills = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    
    # Experience
    total_experience_years = Column(Float, default=0.0)
    work_experience = Column(JSON, default=list)  # List of work experience objects
    
    # Education
    education = Column(JSON, default=list)  # List of education objects
    
    # Projects and achievements
    projects = Column(JSON, default=list)
    achievements = Column(JSON, default=list)
    publications = Column(JSON, default=list)
    
    # Social profiles
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    
    # AI analysis
    ai_score = Column(Float, nullable=True)  # Overall resume score (1-10)
    strengths = Column(JSON, default=list)
    improvement_suggestions = Column(JSON, default=list)
    suitable_roles = Column(JSON, default=list)
    career_level = Column(String(20), nullable=True)  # entry, junior, mid, senior, etc.
    
    # Job matching
    skill_match_score = Column(Float, default=0.0)  # Match score with job requirements
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    
    # Raw data
    raw_text = Column(Text, nullable=True)
    parsing_confidence = Column(Float, nullable=True)  # Confidence score (0-1)
    parsing_errors = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    application = relationship("Application", back_populates="parsed_resume")
    
    def __repr__(self):
        return f"<ParsedResume(id={self.id}, application_id={self.application_id})>"


class Interview(Base):
    """
    Interview scheduling and management
    """
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    interviewer_id = Column(Integer, ForeignKey("recruiter_profiles.id"), nullable=False)
    
    # Interview details
    interview_type = Column(String(20), default=InterviewType.VIDEO)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default="UTC")
    
    # Location/Meeting details
    location = Column(String(500), nullable=True)  # Physical address or meeting link
    meeting_link = Column(String(500), nullable=True)
    meeting_id = Column(String(100), nullable=True)
    meeting_password = Column(String(100), nullable=True)
    
    # Status and feedback
    status = Column(String(20), default=InterviewStatus.SCHEDULED)
    feedback = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)  # 1-5 scale
    
    # Interview questions and responses
    questions = Column(JSON, default=list)
    responses = Column(JSON, default=list)
    
    # Additional interviewers
    additional_interviewers = Column(JSON, default=list)  # List of interviewer IDs
    
    # Reminders
    reminder_sent_candidate = Column(Boolean, default=False)
    reminder_sent_interviewer = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    application = relationship("Application", back_populates="interviews")
    interviewer = relationship("RecruiterProfile", back_populates="conducted_interviews")
    
    def __repr__(self):
        return f"<Interview(id={self.id}, application_id={self.application_id}, status='{self.status}')>"


class ApplicationNote(Base):
    """
    Notes on applications from recruiters
    """
    __tablename__ = "application_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("recruiter_profiles.id"), nullable=False)
    
    # Note content
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, default=True)  # Private to company or visible to candidate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    application = relationship("Application")
    author = relationship("RecruiterProfile")
    
    def __repr__(self):
        return f"<ApplicationNote(id={self.id}, application_id={self.application_id})>"