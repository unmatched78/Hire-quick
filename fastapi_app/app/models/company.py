"""
Company Models

SQLAlchemy models for company management including:
- Company (company information)
- CompanyBenefit (company benefits)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CompanySize(str, enum.Enum):
    """Company size enumeration"""
    STARTUP = "startup"  # 1-10 employees
    SMALL = "small"      # 11-50 employees
    MEDIUM = "medium"    # 51-200 employees
    LARGE = "large"      # 201-1000 employees
    ENTERPRISE = "enterprise"  # 1000+ employees


class CompanyType(str, enum.Enum):
    """Company type enumeration"""
    STARTUP = "startup"
    CORPORATION = "corporation"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"
    AGENCY = "agency"
    CONSULTING = "consulting"
    OTHER = "other"


class Company(Base):
    """
    Company model for storing company information
    """
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    tagline = Column(String(500), nullable=True)
    
    # Company details
    industry = Column(String(100), nullable=True)
    company_size = Column(String(20), default=CompanySize.STARTUP)
    company_type = Column(String(20), default=CompanyType.STARTUP)
    founded_year = Column(Integer, nullable=True)
    
    # Contact information
    website = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Social media
    linkedin_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    instagram_url = Column(String(500), nullable=True)
    
    # Media
    logo = Column(String(500), nullable=True)
    cover_image = Column(String(500), nullable=True)
    
    # Company culture and values
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    values = Column(JSON, default=list)  # List of company values
    culture_keywords = Column(JSON, default=list)  # Keywords describing culture
    
    # Benefits and perks
    benefits = Column(JSON, default=list)  # List of benefits
    perks = Column(JSON, default=list)    # List of perks
    
    # Company metrics
    employee_count = Column(Integer, nullable=True)
    annual_revenue = Column(Float, nullable=True)
    funding_stage = Column(String(50), nullable=True)  # seed, series_a, etc.
    
    # Settings
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    allow_applications = Column(Boolean, default=True)
    
    # SEO and visibility
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recruiters = relationship("RecruiterProfile", back_populates="company")
    jobs = relationship("Job", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
    
    @property
    def full_address(self):
        """Get formatted full address"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(part for part in address_parts if part)
    
    @property
    def location(self):
        """Get formatted location (city, state, country)"""
        location_parts = [self.city, self.state, self.country]
        return ", ".join(part for part in location_parts if part)


class CompanyReview(Base):
    """
    Company reviews from employees/candidates
    """
    __tablename__ = "company_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Ratings (1-5 scale)
    overall_rating = Column(Float, nullable=False)
    culture_rating = Column(Float, nullable=True)
    compensation_rating = Column(Float, nullable=True)
    work_life_balance_rating = Column(Float, nullable=True)
    management_rating = Column(Float, nullable=True)
    career_growth_rating = Column(Float, nullable=True)
    
    # Review metadata
    employment_status = Column(String(50), nullable=True)  # current, former, interviewed
    job_title = Column(String(200), nullable=True)
    employment_duration = Column(String(50), nullable=True)  # 1-2 years, etc.
    
    # Pros and cons
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    advice_to_management = Column(Text, nullable=True)
    
    # Review status
    is_approved = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CompanyReview(id={self.id}, company_id={self.company_id}, rating={self.overall_rating})>"


class CompanyFollower(Base):
    """
    Users following companies for updates
    """
    __tablename__ = "company_followers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Follow settings
    notify_new_jobs = Column(Boolean, default=True)
    notify_company_updates = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CompanyFollower(company_id={self.company_id}, user_id={self.user_id})>"