"""
Background Verification Models

SQLAlchemy models for background verification functionality.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class VerificationStatus(str, enum.Enum):
    """Verification status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VerificationType(str, enum.Enum):
    """Verification type enumeration"""
    IDENTITY = "identity"
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    CRIMINAL = "criminal"
    CREDIT = "credit"
    REFERENCE = "reference"
    PROFESSIONAL_LICENSE = "professional_license"
    DRUG_TEST = "drug_test"


class BackgroundCheck(Base):
    """
    Background verification requests
    """
    __tablename__ = "background_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    requested_by_id = Column(Integer, ForeignKey("recruiter_profiles.id"), nullable=False)
    
    # Check configuration
    verification_types = Column(JSON, default=list)  # List of verification types
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Status and progress
    status = Column(String(20), default=VerificationStatus.PENDING)
    progress_percentage = Column(Integer, default=0)
    
    # Results summary
    overall_result = Column(String(20), nullable=True)  # clear, flagged, failed
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    
    # Provider information
    provider_name = Column(String(100), nullable=True)
    provider_reference = Column(String(100), nullable=True)
    
    # Cost and billing
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    candidate = relationship("CandidateProfile")
    job = relationship("Job")
    requested_by = relationship("RecruiterProfile")
    verifications = relationship("VerificationResult", back_populates="background_check", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BackgroundCheck(id={self.id}, candidate_id={self.candidate_id}, status='{self.status}')>"


class VerificationResult(Base):
    """
    Individual verification results
    """
    __tablename__ = "verification_results"
    
    id = Column(Integer, primary_key=True, index=True)
    background_check_id = Column(Integer, ForeignKey("background_checks.id"), nullable=False)
    
    # Verification details
    verification_type = Column(String(30), nullable=False)
    verification_name = Column(String(200), nullable=False)
    
    # Status and results
    status = Column(String(20), default=VerificationStatus.PENDING)
    result = Column(String(20), nullable=True)  # clear, flagged, failed, unable_to_verify
    
    # Verification data
    data_verified = Column(JSON, default=dict)  # The data that was verified
    findings = Column(JSON, default=list)  # Any findings or discrepancies
    
    # Details and notes
    details = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Provider information
    provider_response = Column(JSON, default=dict)
    provider_reference = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    background_check = relationship("BackgroundCheck", back_populates="verifications")
    
    def __repr__(self):
        return f"<VerificationResult(id={self.id}, type='{self.verification_type}', result='{self.result}')>"


class EmploymentVerification(Base):
    """
    Employment verification details
    """
    __tablename__ = "employment_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_result_id = Column(Integer, ForeignKey("verification_results.id"), nullable=False)
    
    # Employment details to verify
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    salary = Column(Float, nullable=True)
    
    # Verification results
    company_verified = Column(Boolean, nullable=True)
    title_verified = Column(Boolean, nullable=True)
    dates_verified = Column(Boolean, nullable=True)
    salary_verified = Column(Boolean, nullable=True)
    
    # Contact information
    hr_contact_name = Column(String(200), nullable=True)
    hr_contact_email = Column(String(255), nullable=True)
    hr_contact_phone = Column(String(20), nullable=True)
    
    # Verification notes
    verification_notes = Column(Text, nullable=True)
    discrepancies = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    verification_result = relationship("VerificationResult")
    
    def __repr__(self):
        return f"<EmploymentVerification(id={self.id}, company='{self.company_name}')>"


class EducationVerification(Base):
    """
    Education verification details
    """
    __tablename__ = "education_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_result_id = Column(Integer, ForeignKey("verification_results.id"), nullable=False)
    
    # Education details to verify
    institution_name = Column(String(200), nullable=False)
    degree_type = Column(String(100), nullable=False)
    degree_name = Column(String(200), nullable=False)
    field_of_study = Column(String(200), nullable=True)
    graduation_date = Column(DateTime, nullable=True)
    gpa = Column(Float, nullable=True)
    
    # Verification results
    institution_verified = Column(Boolean, nullable=True)
    degree_verified = Column(Boolean, nullable=True)
    dates_verified = Column(Boolean, nullable=True)
    gpa_verified = Column(Boolean, nullable=True)
    
    # Contact information
    registrar_contact = Column(String(200), nullable=True)
    registrar_email = Column(String(255), nullable=True)
    registrar_phone = Column(String(20), nullable=True)
    
    # Verification notes
    verification_notes = Column(Text, nullable=True)
    discrepancies = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    verification_result = relationship("VerificationResult")
    
    def __repr__(self):
        return f"<EducationVerification(id={self.id}, institution='{self.institution_name}')>"


class ReferenceCheck(Base):
    """
    Reference check details
    """
    __tablename__ = "reference_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_result_id = Column(Integer, ForeignKey("verification_results.id"), nullable=False)
    
    # Reference details
    reference_name = Column(String(200), nullable=False)
    reference_title = Column(String(200), nullable=True)
    reference_company = Column(String(200), nullable=True)
    reference_email = Column(String(255), nullable=True)
    reference_phone = Column(String(20), nullable=True)
    
    # Relationship to candidate
    relationship_type = Column(String(50), nullable=True)  # supervisor, colleague, client, etc.
    relationship_duration = Column(String(50), nullable=True)
    
    # Reference check results
    contacted_successfully = Column(Boolean, default=False)
    willing_to_provide_reference = Column(Boolean, nullable=True)
    
    # Ratings (1-5 scale)
    overall_rating = Column(Float, nullable=True)
    work_quality_rating = Column(Float, nullable=True)
    reliability_rating = Column(Float, nullable=True)
    teamwork_rating = Column(Float, nullable=True)
    communication_rating = Column(Float, nullable=True)
    
    # Feedback
    strengths = Column(JSON, default=list)
    areas_for_improvement = Column(JSON, default=list)
    would_rehire = Column(Boolean, nullable=True)
    additional_comments = Column(Text, nullable=True)
    
    # Contact attempts
    contact_attempts = Column(Integer, default=0)
    last_contact_attempt = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    verification_result = relationship("VerificationResult")
    
    def __repr__(self):
        return f"<ReferenceCheck(id={self.id}, reference='{self.reference_name}')>"