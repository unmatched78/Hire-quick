"""
User Pydantic Schemas

Request and response models for user-related API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserType(str, Enum):
    """User type enumeration"""
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: Optional[str] = None
    user_type: UserType = UserType.CANDIDATE
    phone: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# Authentication schemas
class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Profile schemas
class CandidateProfileBase(BaseModel):
    """Base candidate profile schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    current_title: Optional[str] = None
    summary: Optional[str] = None
    experience_years: int = 0
    salary_expectation: Optional[int] = None
    availability: Optional[str] = None
    skills: List[str] = []
    preferred_locations: List[str] = []
    preferred_job_types: List[str] = []
    remote_preference: str = "hybrid"
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    profile_visibility: str = "public"
    allow_contact: bool = True


class CandidateProfileCreate(CandidateProfileBase):
    """Candidate profile creation schema"""
    pass


class CandidateProfileUpdate(BaseModel):
    """Candidate profile update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    current_title: Optional[str] = None
    summary: Optional[str] = None
    experience_years: Optional[int] = None
    salary_expectation: Optional[int] = None
    availability: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    profile_visibility: Optional[str] = None
    allow_contact: Optional[bool] = None


class CandidateProfileResponse(CandidateProfileBase):
    """Candidate profile response schema"""
    id: int
    user_id: int
    profile_completed: bool
    completion_percentage: int
    profile_picture: Optional[str] = None
    resume_file: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RecruiterProfileBase(BaseModel):
    """Base recruiter profile schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    phone_extension: Optional[str] = None
    bio: Optional[str] = None


class RecruiterProfileCreate(RecruiterProfileBase):
    """Recruiter profile creation schema"""
    company_id: Optional[int] = None


class RecruiterProfileUpdate(BaseModel):
    """Recruiter profile update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    phone_extension: Optional[str] = None
    bio: Optional[str] = None
    company_id: Optional[int] = None
    can_post_jobs: Optional[bool] = None
    can_view_applications: Optional[bool] = None
    can_schedule_interviews: Optional[bool] = None
    can_make_offers: Optional[bool] = None


class RecruiterProfileResponse(RecruiterProfileBase):
    """Recruiter profile response schema"""
    id: int
    user_id: int
    company_id: Optional[int] = None
    profile_completed: bool
    profile_picture: Optional[str] = None
    can_post_jobs: bool
    can_view_applications: bool
    can_schedule_interviews: bool
    can_make_offers: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Complete user schemas with profiles
class UserWithProfileResponse(UserResponse):
    """User response with profile data"""
    candidate_profile: Optional[CandidateProfileResponse] = None
    recruiter_profile: Optional[RecruiterProfileResponse] = None


# File upload schemas
class FileUploadResponse(BaseModel):
    """File upload response schema"""
    filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_url: Optional[str] = None


class ProfilePictureUploadResponse(FileUploadResponse):
    """Profile picture upload response schema"""
    thumbnail_url: Optional[str] = None


class ResumeUploadResponse(FileUploadResponse):
    """Resume upload response schema"""
    parsing_status: str = "pending"
    parsed_data: Optional[dict] = None