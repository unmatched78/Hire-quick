"""
API v1 Router

Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter
from .endpoints import auth, users, jobs, applications, companies, analytics, ai, files

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["Jobs"]
)

api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["Applications"]
)

api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics & Reporting"]
)

api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI-Powered Features"]
)

api_router.include_router(
    files.router,
    prefix="/files",
    tags=["File Management"]
)