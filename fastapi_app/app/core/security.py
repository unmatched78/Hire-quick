"""
Security utilities for authentication and authorization

Includes JWT token handling, password hashing, and security dependencies.
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .exceptions import AuthenticationException, AuthorizationException
from ..models.user import User, UserType

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        
    Returns:
        str: JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        
    Returns:
        str: JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        Optional[User]: User if found
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Optional[User]: User if found
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str
) -> Optional[User]:
    """
    Authenticate user with email and password
    
    Args:
        db: Database session
        email: User email
        password: User password
        
    Returns:
        Optional[User]: User if authenticated
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        AuthenticationException: If token is invalid or user not found
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationException("Invalid token")
            
        # Check if it's a refresh token
        token_type = payload.get("type")
        if token_type == "refresh":
            raise AuthenticationException("Refresh token cannot be used for authentication")
            
    except JWTError:
        raise AuthenticationException("Invalid token")
    
    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise AuthenticationException("User not found")
    
    if not user.is_active:
        raise AuthenticationException("User account is disabled")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from token
        
    Returns:
        User: Current active user
        
    Raises:
        AuthenticationException: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationException("User account is disabled")
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current verified user
        
    Raises:
        AuthenticationException: If user is not verified
    """
    if not current_user.is_verified:
        raise AuthenticationException("Email verification required")
    return current_user


def require_user_type(allowed_types: list[UserType]):
    """
    Dependency factory to require specific user types
    
    Args:
        allowed_types: List of allowed user types
        
    Returns:
        Dependency function
    """
    async def check_user_type(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        if current_user.user_type not in allowed_types:
            raise AuthorizationException(
                f"Access denied. Required user types: {', '.join(allowed_types)}"
            )
        return current_user
    
    return check_user_type


# Common user type dependencies
require_candidate = require_user_type([UserType.CANDIDATE])
require_recruiter = require_user_type([UserType.RECRUITER])
require_admin = require_user_type([UserType.ADMIN])
require_recruiter_or_admin = require_user_type([UserType.RECRUITER, UserType.ADMIN])


async def get_current_superuser(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """
    Get current superuser
    
    Args:
        current_user: Current verified user
        
    Returns:
        User: Current superuser
        
    Raises:
        AuthorizationException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise AuthorizationException("Superuser access required")
    return current_user


def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return payload
    
    Args:
        token: JWT token
        
    Returns:
        Optional[dict]: Token payload if valid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """
    Create password reset token
    
    Args:
        email: User email
        
    Returns:
        str: Password reset token
    """
    delta = timedelta(hours=24)  # Token valid for 24 hours
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token
    
    Args:
        token: Password reset token
        
    Returns:
        Optional[str]: Email if token is valid
    """
    try:
        decoded_token = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Check token type
        if decoded_token.get("type") != "password_reset":
            return None
            
        return decoded_token.get("sub")
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """
    Create email verification token
    
    Args:
        email: User email
        
    Returns:
        str: Email verification token
    """
    delta = timedelta(hours=48)  # Token valid for 48 hours
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "email_verification"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify email verification token
    
    Args:
        token: Email verification token
        
    Returns:
        Optional[str]: Email if token is valid
    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Check token type
        if decoded_token.get("type") != "email_verification":
            return None
            
        return decoded_token.get("sub")
    except JWTError:
        return None