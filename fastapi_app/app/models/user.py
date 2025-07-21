"""
User Models

SQLAlchemy models for user management including:
- User (base user model)
- CandidateProfile (candidate-specific data)
- RecruiterProfile (recruiter-specific data)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserType(str, enum.Enum):
    """User type enumeration"""
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class User(Base):
    """
    Base user model for authentication and basic user data
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User type and status
    user_type = Column(String(20), default=UserType.CANDIDATE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_token = Column(String(255), nullable=True)
    
    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    candidate_profile = relationship("CandidateProfile", back_populates="user", uselist=False)
    recruiter_profile = relationship("RecruiterProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', type='{self.user_type}')>"


class CandidateProfile(Base):
    """
    Candidate profile with job seeker specific information
    """
    __tablename__ = "candidate_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # Professional information
    current_title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)
    salary_expectation = Column(Integer, nullable=True)
    availability = Column(String(100), nullable=True)  # immediate, 2_weeks, 1_month, etc.
    
    # Skills and preferences
    skills = Column(JSON, default=list)  # List of skills
    preferred_locations = Column(JSON, default=list)  # Preferred work locations
    preferred_job_types = Column(JSON, default=list)  # full-time, part-time, contract, etc.
    remote_preference = Column(String(20), default="hybrid")  # remote, onsite, hybrid
    
    # Social profiles
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    
    # Files
    profile_picture = Column(String(500), nullable=True)
    resume_file = Column(String(500), nullable=True)
    
    # Profile completion
    profile_completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)
    
    # Privacy settings
    profile_visibility = Column(String(20), default="public")  # public, private, recruiters_only
    allow_contact = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    applications = relationship("Application", back_populates="candidate")
    saved_jobs = relationship("SavedJob", back_populates="candidate")
    
    def __repr__(self):
        return f"<CandidateProfile(id={self.id}, name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email.split('@')[0] if self.user else "Unknown"


class RecruiterProfile(Base):
    """
    Recruiter profile with hiring manager specific information
    """
    __tablename__ = "recruiter_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Personal information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    title = Column(String(200), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Contact information
    phone_extension = Column(String(20), nullable=True)
    
    # Profile
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    
    # Permissions and settings
    can_post_jobs = Column(Boolean, default=True)
    can_view_applications = Column(Boolean, default=True)
    can_schedule_interviews = Column(Boolean, default=True)
    can_make_offers = Column(Boolean, default=False)
    
    # Profile completion
    profile_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recruiter_profile")
    company = relationship("Company", back_populates="recruiters")
    posted_jobs = relationship("Job", back_populates="recruiter")
    conducted_interviews = relationship("Interview", back_populates="interviewer")
    
    def __repr__(self):
        return f"<RecruiterProfile(id={self.id}, name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email.split('@')[0] if self.user else "Unknown"


class UserSession(Base):
    """
    User session tracking for security and analytics
    """
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session information
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=True)
    
    # Device and location information
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    location = Column(String(200), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"