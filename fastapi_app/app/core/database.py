"""
Database Configuration and Setup

SQLAlchemy async database setup with SQLite support.
Includes database initialization and session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DATABASE_ECHO,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create declarative base
Base = declarative_base()


# SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite"""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    
    Creates all tables defined in the models.
    """
    try:
        # Import all models to ensure they are registered
        from app.models import (
            user, company, job, application, 
            talent_pool, background_verification
        )
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def drop_db():
    """
    Drop all database tables
    
    WARNING: This will delete all data!
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            
        logger.info("Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Error dropping database: {e}")
        raise


async def reset_db():
    """
    Reset database by dropping and recreating all tables
    
    WARNING: This will delete all data!
    """
    await drop_db()
    await init_db()
    logger.info("Database reset completed")