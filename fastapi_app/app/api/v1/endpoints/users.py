"""
User Management Endpoints

Handles user profile management and user-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_candidate, require_recruiter
from app.core.exceptions import NotFoundException, ValidationException
from app.models.user import User, CandidateProfile, RecruiterProfile
from app.schemas.user import (
    UserResponse,
    UserWithProfileResponse,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    RecruiterProfileResponse,
    RecruiterProfileUpdate,
    ChangePasswordRequest,
    FileUploadResponse
)

router = APIRouter()


@router.get("/me", response_model=UserWithProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user with profile information
    
    Returns the current user's information along with their profile data.
    """
    # Load profile based on user type
    if current_user.user_type == "candidate":
        result = await db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
        )
        profile = result.scalar_one_or_none()
        
        return UserWithProfileResponse(
            **current_user.__dict__,
            candidate_profile=CandidateProfileResponse.from_orm(profile) if profile else None
        )
    
    elif current_user.user_type == "recruiter":
        result = await db.execute(
            select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        )
        profile = result.scalar_one_or_none()
        
        return UserWithProfileResponse(
            **current_user.__dict__,
            recruiter_profile=RecruiterProfileResponse.from_orm(profile) if profile else None
        )
    
    return UserWithProfileResponse(**current_user.__dict__)


@router.put("/candidate-profile", response_model=CandidateProfileResponse)
async def update_candidate_profile(
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
):
    """
    Update candidate profile
    
    Updates the current candidate's profile information.
    """
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise NotFoundException("Candidate profile not found")
    
    # Update profile fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    # Calculate completion percentage
    profile.completion_percentage = calculate_profile_completion(profile)
    profile.profile_completed = profile.completion_percentage >= 80
    
    await db.commit()
    await db.refresh(profile)
    
    return CandidateProfileResponse.from_orm(profile)


@router.put("/recruiter-profile", response_model=RecruiterProfileResponse)
async def update_recruiter_profile(
    profile_data: RecruiterProfileUpdate,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
):
    """
    Update recruiter profile
    
    Updates the current recruiter's profile information.
    """
    result = await db.execute(
        select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise NotFoundException("Recruiter profile not found")
    
    # Update profile fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    # Check if profile is completed
    required_fields = ['first_name', 'last_name', 'title']
    profile.profile_completed = all(getattr(profile, field) for field in required_fields)
    
    await db.commit()
    await db.refresh(profile)
    
    return RecruiterProfileResponse.from_orm(profile)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    
    Changes the current user's password after verifying the current password.
    """
    from app.core.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise ValidationException("Current password is incorrect")
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/upload-profile-picture", response_model=FileUploadResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload profile picture
    
    Uploads and sets a profile picture for the current user.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise ValidationException("Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.")
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise ValidationException("File too large. Maximum size is 5MB.")
    
    # Save file (simplified - in production, use cloud storage)
    import os
    from pathlib import Path
    import uuid
    
    upload_dir = Path("media/profile_pictures")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{current_user.id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Update user profile
    if current_user.user_type == "candidate":
        result = await db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            profile.profile_picture = str(file_path)
    
    elif current_user.user_type == "recruiter":
        result = await db.execute(
            select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            profile.profile_picture = str(file_path)
    
    await db.commit()
    
    return FileUploadResponse(
        filename=filename,
        file_path=str(file_path),
        file_size=len(file_content),
        content_type=file.content_type,
        upload_url=f"/media/profile_pictures/{filename}"
    )


def calculate_profile_completion(profile: CandidateProfile) -> int:
    """Calculate candidate profile completion percentage"""
    fields = [
        profile.first_name,
        profile.last_name,
        profile.location,
        profile.current_title,
        profile.summary,
        profile.skills,
        profile.experience_years > 0,
        profile.linkedin_url or profile.github_url or profile.portfolio_url
    ]
    
    completed = sum(1 for field in fields if field)
    return int((completed / len(fields)) * 100)