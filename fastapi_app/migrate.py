#!/usr/bin/env python3
"""
Database Migration Script

This script initializes the database and creates all tables.
Run this before starting the application for the first time.
"""

import asyncio
import logging
from app.core.database import init_db, engine
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def create_tables():
    """Create all database tables"""
    try:
        logger.info("Starting database migration...")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
        # Initialize database
        await init_db()
        
        logger.info("Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise
    finally:
        # Close the engine
        await engine.dispose()


async def create_sample_data():
    """Create sample data for testing (optional)"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import get_db_session
    from app.models.user import User, CandidateProfile, RecruiterProfile
    from app.models.company import Company
    from app.models.job import Job
    from app.core.security import get_password_hash
    from datetime import datetime
    
    try:
        logger.info("Creating sample data...")
        
        async with get_db_session() as db:
            # Create a sample company
            company = Company(
                name="Tech Innovations Inc",
                slug="tech-innovations-inc",
                description="A leading technology company focused on innovation",
                industry="Technology",
                company_size="medium",
                website="https://techinnovations.com",
                location="San Francisco, CA",
                is_active=True,
                is_verified=True
            )
            db.add(company)
            await db.flush()
            
            # Create a sample recruiter
            recruiter_user = User(
                email="recruiter@techinnovations.com",
                username="recruiter1",
                hashed_password=get_password_hash("password123"),
                user_type="recruiter",
                is_active=True,
                is_verified=True,
                email_verified_at=datetime.utcnow()
            )
            db.add(recruiter_user)
            await db.flush()
            
            recruiter_profile = RecruiterProfile(
                user_id=recruiter_user.id,
                company_id=company.id,
                first_name="Jane",
                last_name="Smith",
                title="Senior Technical Recruiter",
                can_post_jobs=True,
                profile_completed=True
            )
            db.add(recruiter_profile)
            await db.flush()
            
            # Create a sample candidate
            candidate_user = User(
                email="candidate@example.com",
                username="candidate1",
                hashed_password=get_password_hash("password123"),
                user_type="candidate",
                is_active=True,
                is_verified=True,
                email_verified_at=datetime.utcnow()
            )
            db.add(candidate_user)
            await db.flush()
            
            candidate_profile = CandidateProfile(
                user_id=candidate_user.id,
                first_name="John",
                last_name="Doe",
                location="New York, NY",
                current_title="Software Engineer",
                summary="Experienced full-stack developer with 5+ years of experience",
                skills=["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
                experience_years=5,
                linkedin_url="https://linkedin.com/in/johndoe",
                github_url="https://github.com/johndoe",
                completion_percentage=85,
                profile_completed=True
            )
            db.add(candidate_profile)
            await db.flush()
            
            # Create sample jobs
            jobs_data = [
                {
                    "title": "Senior Python Developer",
                    "description": "We are looking for an experienced Python developer to join our backend team. You will be responsible for developing and maintaining our API services using FastAPI and working with modern cloud technologies.",
                    "summary": "Senior Python Developer position with focus on FastAPI and cloud technologies",
                    "location": "San Francisco, CA",
                    "job_type": "full_time",
                    "remote_type": "hybrid",
                    "salary_min": 120000,
                    "salary_max": 160000,
                    "requirements": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
                    "benefits": ["Health Insurance", "401k", "Flexible Hours", "Remote Work"],
                    "status": "active"
                },
                {
                    "title": "Frontend React Developer",
                    "description": "Join our frontend team to build amazing user experiences. You will work with React, TypeScript, and modern frontend tools to create responsive and intuitive web applications.",
                    "summary": "Frontend React Developer for building modern web applications",
                    "location": "Remote",
                    "job_type": "full_time",
                    "remote_type": "remote",
                    "salary_min": 90000,
                    "salary_max": 130000,
                    "requirements": ["React", "TypeScript", "HTML/CSS", "Git"],
                    "benefits": ["Health Insurance", "Remote Work", "Learning Budget"],
                    "status": "active"
                },
                {
                    "title": "DevOps Engineer",
                    "description": "We need a DevOps engineer to help us scale our infrastructure. You will work with Kubernetes, AWS, and CI/CD pipelines to ensure our applications run smoothly.",
                    "summary": "DevOps Engineer for infrastructure scaling and automation",
                    "location": "San Francisco, CA",
                    "job_type": "full_time",
                    "remote_type": "onsite",
                    "salary_min": 110000,
                    "salary_max": 150000,
                    "requirements": ["Kubernetes", "AWS", "Docker", "Terraform", "CI/CD"],
                    "benefits": ["Health Insurance", "401k", "Stock Options"],
                    "status": "active"
                }
            ]
            
            for job_data in jobs_data:
                job = Job(
                    company_id=company.id,
                    recruiter_id=recruiter_profile.id,
                    **job_data
                )
                db.add(job)
            
            await db.commit()
            logger.info("Sample data created successfully!")
            
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise


async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Script")
    parser.add_argument(
        "--sample-data", 
        action="store_true", 
        help="Create sample data for testing"
    )
    
    args = parser.parse_args()
    
    # Create tables
    await create_tables()
    
    # Create sample data if requested
    if args.sample_data:
        await create_sample_data()
    
    logger.info("Migration completed!")


if __name__ == "__main__":
    asyncio.run(main())