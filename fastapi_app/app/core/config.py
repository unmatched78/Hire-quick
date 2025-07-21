"""
Application Configuration

Centralized configuration management using Pydantic settings.
Supports environment variables and .env files.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Hire Quick - Recruitment Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=12000, description="Server port")
    ALLOWED_HOSTS: str = Field(
        default="*", 
        description="Allowed hosts for CORS (comma-separated)"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./hire_quick.db",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # Password hashing
    PWD_CONTEXT_SCHEMES: List[str] = Field(
        default=["bcrypt"],
        description="Password hashing schemes"
    )
    PWD_CONTEXT_DEPRECATED: str = Field(
        default="auto",
        description="Deprecated password schemes"
    )
    
    # File Upload
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file upload size in bytes"
    )
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[
            "pdf", "doc", "docx", "txt", "rtf",  # Documents
            "jpg", "jpeg", "png", "gif", "webp",  # Images
            "mp4", "avi", "mov", "wmv",  # Videos
            "mp3", "wav", "m4a", "flac"  # Audio
        ],
        description="Allowed file extensions for uploads"
    )
    
    # Directories
    UPLOAD_DIR: str = Field(default="media/uploads", description="Upload directory")
    STATIC_DIR: str = Field(default="static", description="Static files directory")
    LOGS_DIR: str = Field(default="logs", description="Logs directory")
    
    # Email Configuration
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_USE_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    FROM_EMAIL: str = Field(
        default="noreply@hirequick.com",
        description="Default from email address"
    )
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI features"
    )
    AI_ENABLED: bool = Field(
        default=False,
        description="Enable AI features"
    )
    
    # Background Tasks
    CELERY_BROKER_URL: Optional[str] = Field(
        default=None,
        description="Celery broker URL (Redis/RabbitMQ)"
    )
    CELERY_RESULT_BACKEND: Optional[str] = Field(
        default=None,
        description="Celery result backend URL"
    )
    
    # Cache Configuration
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis URL for caching"
    )
    CACHE_TTL: int = Field(
        default=300,
        description="Default cache TTL in seconds"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Number of requests per time window"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60,
        description="Rate limit time window in seconds"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # WebSocket
    WEBSOCKET_ENABLED: bool = Field(
        default=True,
        description="Enable WebSocket support"
    )
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )
    
    def get_allowed_hosts(self) -> List[str]:
        """Get allowed hosts as a list"""
        if self.ALLOWED_HOSTS == "*":
            return ["*"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    @validator("AI_ENABLED", pre=True, always=True)
    def set_ai_enabled(cls, v, values):
        """Enable AI features if OpenAI API key is provided"""
        if values.get("OPENAI_API_KEY"):
            return True
        return v
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.UPLOAD_DIR,
            self.STATIC_DIR,
            self.LOGS_DIR,
            f"{self.UPLOAD_DIR}/resumes",
            f"{self.UPLOAD_DIR}/profiles",
            f"{self.UPLOAD_DIR}/applications",
            f"{self.UPLOAD_DIR}/companies"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()