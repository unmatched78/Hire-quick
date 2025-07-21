"""
Authentication Endpoints

Handles user authentication, registration, password reset, and email verification.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password_reset_token,
    create_password_reset_token,
    verify_email_verification_token,
    create_email_verification_token,
    get_current_user,
    verify_token
)
from app.core.config import settings
from app.core.exceptions import (
    ValidationException,
    AuthenticationException,
    ConflictException,
    NotFoundException
)
from app.models.user import User, CandidateProfile, RecruiterProfile
from app.schemas.user import (
    UserCreate,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    UserResponse
)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    Creates a new user account and sends email verification.
    Automatically creates the appropriate profile based on user type.
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise ConflictException("User with this email already exists")
    
    # Check username uniqueness if provided
    if user_data.username:
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        existing_username = result.scalar_one_or_none()
        
        if existing_username:
            raise ConflictException("Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        user_type=user_data.user_type,
        phone=user_data.phone,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    await db.flush()  # Get the user ID
    
    # Create appropriate profile
    if user_data.user_type == "candidate":
        profile = CandidateProfile(user_id=db_user.id)
        db.add(profile)
    elif user_data.user_type == "recruiter":
        profile = RecruiterProfile(user_id=db_user.id)
        db.add(profile)
    
    await db.commit()
    await db.refresh(db_user)
    
    # Send email verification (background task)
    verification_token = create_email_verification_token(user_data.email)
    # background_tasks.add_task(send_verification_email, user_data.email, verification_token)
    
    # Create user response data manually to avoid SQLAlchemy session issues
    response_data = {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "user_type": db_user.user_type,
        "phone": db_user.phone,
        "is_active": db_user.is_active,
        "is_verified": db_user.is_verified,
        "is_superuser": db_user.is_superuser,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "last_login": db_user.last_login
    }
    
    return UserResponse(**response_data)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    User login
    
    Authenticates user and returns access and refresh tokens.
    """
    user = await authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise AuthenticationException("Invalid email or password")
    
    if not user.is_active:
        raise AuthenticationException("Account is disabled")
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(subject=user.id)
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    # Create user response data manually to avoid SQLAlchemy session issues
    user_data = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "user_type": user.user_type,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login
    }
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user_data)
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token
    
    Uses refresh token to generate a new access token.
    """
    payload = verify_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationException("Invalid refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid refresh token")
    
    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise AuthenticationException("User not found or inactive")
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset
    
    Sends password reset email if user exists.
    Always returns success to prevent email enumeration.
    """
    result = await db.execute(
        select(User).where(User.email == reset_data.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        reset_token = create_password_reset_token(reset_data.email)
        # background_tasks.add_task(send_password_reset_email, reset_data.email, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm password reset
    
    Resets user password using the reset token.
    """
    email = verify_password_reset_token(reset_data.token)
    
    if not email:
        raise AuthenticationException("Invalid or expired reset token")
    
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundException("User not found")
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    
    await db.commit()
    
    return {"message": "Password reset successfully"}


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email address
    
    Verifies user email using the verification token.
    """
    email = verify_email_verification_token(verification_data.token)
    
    if not email:
        raise AuthenticationException("Invalid or expired verification token")
    
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundException("User not found")
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Verify email
    from datetime import datetime
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.verification_token = None
    
    await db.commit()
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification_email(
    email_data: PasswordResetRequest,  # Reuse schema for email
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend email verification
    
    Sends a new verification email if user exists and is not verified.
    """
    result = await db.execute(
        select(User).where(User.email == email_data.email)
    )
    user = result.scalar_one_or_none()
    
    if user and not user.is_verified:
        verification_token = create_email_verification_token(email_data.email)
        # background_tasks.add_task(send_verification_email, email_data.email, verification_token)
    
    return {"message": "If the email exists and is not verified, a verification link has been sent"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    User logout
    
    In a stateless JWT system, logout is handled client-side by discarding tokens.
    This endpoint exists for consistency and future token blacklisting.
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Returns the current authenticated user's information.
    """
    # Create user response data manually to avoid SQLAlchemy session issues
    response_data = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "user_type": current_user.user_type,
        "phone": current_user.phone,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "last_login": current_user.last_login
    }
    
    return UserResponse(**response_data)