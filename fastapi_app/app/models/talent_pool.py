"""
Talent Pool Models

SQLAlchemy models for talent pool and matching functionality.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class MatchStatus(str, enum.Enum):
    """Match status enumeration"""
    PENDING = "pending"
    VIEWED = "viewed"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CONTACTED = "contacted"
    EXPIRED = "expired"


class TalentPoolEntry(Base):
    """
    Talent pool entries for candidates
    """
    __tablename__ = "talent_pool_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), unique=True, nullable=False)
    
    # Pool settings
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    availability_date = Column(DateTime(timezone=True), nullable=True)
    
    # Visibility settings
    profile_visibility = Column(String(20), default="public")  # public, private, recruiters_only
    allow_contact = Column(Boolean, default=True)
    
    # Preferences
    preferred_roles = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)
    preferred_companies = Column(JSON, default=list)
    preferred_salary_min = Column(Integer, nullable=True)
    preferred_salary_max = Column(Integer, nullable=True)
    
    # Matching settings
    auto_matching_enabled = Column(Boolean, default=True)
    match_score_threshold = Column(Float, default=0.5)  # Minimum match score (0-1)
    
    # Analytics
    profile_views = Column(Integer, default=0)
    contact_requests = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("CandidateProfile")
    matches = relationship("JobMatch", back_populates="talent_entry")
    
    def __repr__(self):
        return f"<TalentPoolEntry(id={self.id}, candidate_id={self.candidate_id})>"


class JobMatch(Base):
    """
    AI-generated job matches for candidates
    """
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    talent_entry_id = Column(Integer, ForeignKey("talent_pool_entries.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Match scoring
    overall_score = Column(Float, nullable=False)  # Overall match score (0-1)
    skill_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    salary_score = Column(Float, default=0.0)
    culture_score = Column(Float, default=0.0)
    
    # Match details
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    skill_gaps = Column(JSON, default=list)
    
    # Match reasons
    match_reasons = Column(JSON, default=list)  # Why this is a good match
    concerns = Column(JSON, default=list)  # Potential concerns
    
    # Status and interaction
    status = Column(String(20), default=MatchStatus.PENDING)
    viewed_by_candidate = Column(Boolean, default=False)
    viewed_by_recruiter = Column(Boolean, default=False)
    
    # Feedback
    candidate_feedback = Column(String(20), nullable=True)  # interested, not_interested
    recruiter_feedback = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    talent_entry = relationship("TalentPoolEntry", back_populates="matches")
    job = relationship("Job")
    
    def __repr__(self):
        return f"<JobMatch(id={self.id}, score={self.overall_score:.2f})>"


class SkillAssessment(Base):
    """
    Skill assessments for candidates
    """
    __tablename__ = "skill_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    
    # Assessment details
    skill_name = Column(String(100), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # quiz, coding, project, etc.
    
    # Results
    score = Column(Float, nullable=True)  # Score (0-100)
    max_score = Column(Float, default=100.0)
    passed = Column(Boolean, default=False)
    
    # Assessment data
    questions = Column(JSON, default=list)
    answers = Column(JSON, default=list)
    time_taken_minutes = Column(Integer, nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(100), nullable=True)  # Platform or organization
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    candidate = relationship("CandidateProfile")
    
    def __repr__(self):
        return f"<SkillAssessment(id={self.id}, skill='{self.skill_name}', score={self.score})>"


class CandidateRanking(Base):
    """
    AI-generated candidate rankings for jobs
    """
    __tablename__ = "candidate_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    
    # Ranking details
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # Overall score (0-1)
    
    # Score breakdown
    skill_match_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    availability_score = Column(Float, default=0.0)
    
    # Analysis
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job")
    candidate = relationship("CandidateProfile")
    
    def __repr__(self):
        return f"<CandidateRanking(job_id={self.job_id}, candidate_id={self.candidate_id}, rank={self.rank})>"