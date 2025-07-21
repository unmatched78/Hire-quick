"""
Analytics Service

Analytics and reporting service for recruitment metrics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
import logging

from ..models.user import User
from ..models.job import Job
from ..models.application import Application
from ..models.company import Company

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Analytics and reporting service"""
    
    async def get_dashboard_stats(self, db: AsyncSession, user_id: int, user_type: str) -> Dict[str, Any]:
        """
        Get dashboard statistics based on user type
        
        Args:
            db: Database session
            user_id: User ID
            user_type: Type of user (candidate, recruiter, admin)
            
        Returns:
            Dashboard statistics
        """
        try:
            if user_type == 'candidate':
                return await self._get_candidate_dashboard_stats(db, user_id)
            elif user_type == 'recruiter':
                return await self._get_recruiter_dashboard_stats(db, user_id)
            elif user_type == 'admin':
                return await self._get_admin_dashboard_stats(db)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}

    async def _get_candidate_dashboard_stats(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get candidate dashboard statistics"""
        stats = {}
        
        # Total applications
        total_apps_query = select(func.count(Application.id)).where(Application.candidate_id == user_id)
        result = await db.execute(total_apps_query)
        stats['total_applications'] = result.scalar() or 0
        
        # Applications by status
        status_query = select(
            Application.status,
            func.count(Application.id).label('count')
        ).where(Application.candidate_id == user_id).group_by(Application.status)
        
        result = await db.execute(status_query)
        status_counts = {row.status: row.count for row in result}
        stats['applications_by_status'] = status_counts
        
        # Recent applications (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_apps_query = select(func.count(Application.id)).where(
            and_(
                Application.candidate_id == user_id,
                Application.applied_at >= thirty_days_ago
            )
        )
        result = await db.execute(recent_apps_query)
        stats['recent_applications'] = result.scalar() or 0
        
        # Interview count
        interview_query = select(func.count(Application.id)).where(
            and_(
                Application.candidate_id == user_id,
                Application.status.in_(['interview_scheduled', 'interviewed'])
            )
        )
        result = await db.execute(interview_query)
        stats['interviews'] = result.scalar() or 0
        
        # Response rate (applications with response vs total)
        responded_query = select(func.count(Application.id)).where(
            and_(
                Application.candidate_id == user_id,
                Application.status != 'submitted'
            )
        )
        result = await db.execute(responded_query)
        responded_count = result.scalar() or 0
        
        total_count = stats['total_applications']
        stats['response_rate'] = (responded_count / total_count * 100) if total_count > 0 else 0
        
        # Application trends (last 6 months by month)
        stats['application_trends'] = await self._get_application_trends(db, user_id, 'candidate')
        
        return stats

    async def _get_recruiter_dashboard_stats(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get recruiter dashboard statistics"""
        stats = {}
        
        # Get recruiter's company
        user_query = select(User).where(User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        
        if not user or not user.recruiter_profile:
            return stats
        
        company_id = user.recruiter_profile.get('company_id')
        if not company_id:
            return stats
        
        # Total jobs posted
        total_jobs_query = select(func.count(Job.id)).where(Job.company_id == company_id)
        result = await db.execute(total_jobs_query)
        stats['total_jobs'] = result.scalar() or 0
        
        # Active jobs
        active_jobs_query = select(func.count(Job.id)).where(
            and_(Job.company_id == company_id, Job.status == 'published')
        )
        result = await db.execute(active_jobs_query)
        stats['active_jobs'] = result.scalar() or 0
        
        # Total applications received
        apps_query = select(func.count(Application.id)).join(Job).where(Job.company_id == company_id)
        result = await db.execute(apps_query)
        stats['total_applications'] = result.scalar() or 0
        
        # Applications by status
        status_query = select(
            Application.status,
            func.count(Application.id).label('count')
        ).join(Job).where(Job.company_id == company_id).group_by(Application.status)
        
        result = await db.execute(status_query)
        status_counts = {row.status: row.count for row in result}
        stats['applications_by_status'] = status_counts
        
        # Recent applications (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_apps_query = select(func.count(Application.id)).join(Job).where(
            and_(
                Job.company_id == company_id,
                Application.applied_at >= seven_days_ago
            )
        )
        result = await db.execute(recent_apps_query)
        stats['recent_applications'] = result.scalar() or 0
        
        # Interviews scheduled
        interview_query = select(func.count(Application.id)).join(Job).where(
            and_(
                Job.company_id == company_id,
                Application.status.in_(['interview_scheduled', 'interviewed'])
            )
        )
        result = await db.execute(interview_query)
        stats['interviews_scheduled'] = result.scalar() or 0
        
        # Hiring metrics
        stats['hiring_metrics'] = await self._get_hiring_metrics(db, company_id)
        
        # Top performing jobs
        stats['top_jobs'] = await self._get_top_performing_jobs(db, company_id)
        
        return stats

    async def _get_admin_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        stats = {}
        
        # Total users
        total_users_query = select(func.count(User.id))
        result = await db.execute(total_users_query)
        stats['total_users'] = result.scalar() or 0
        
        # Users by type
        user_type_query = select(
            User.user_type,
            func.count(User.id).label('count')
        ).group_by(User.user_type)
        
        result = await db.execute(user_type_query)
        user_counts = {row.user_type: row.count for row in result}
        stats['users_by_type'] = user_counts
        
        # Total companies
        total_companies_query = select(func.count(Company.id))
        result = await db.execute(total_companies_query)
        stats['total_companies'] = result.scalar() or 0
        
        # Total jobs
        total_jobs_query = select(func.count(Job.id))
        result = await db.execute(total_jobs_query)
        stats['total_jobs'] = result.scalar() or 0
        
        # Active jobs
        active_jobs_query = select(func.count(Job.id)).where(Job.status == 'published')
        result = await db.execute(active_jobs_query)
        stats['active_jobs'] = result.scalar() or 0
        
        # Total applications
        total_apps_query = select(func.count(Application.id))
        result = await db.execute(total_apps_query)
        stats['total_applications'] = result.scalar() or 0
        
        # Platform growth metrics
        stats['growth_metrics'] = await self._get_platform_growth_metrics(db)
        
        # Popular job categories
        stats['popular_categories'] = await self._get_popular_job_categories(db)
        
        return stats

    async def _get_application_trends(self, db: AsyncSession, user_id: int, user_type: str) -> List[Dict[str, Any]]:
        """Get application trends over time"""
        try:
            # Get data for last 6 months
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            
            if user_type == 'candidate':
                query = select(
                    func.date_trunc('month', Application.applied_at).label('month'),
                    func.count(Application.id).label('count')
                ).where(
                    and_(
                        Application.candidate_id == user_id,
                        Application.applied_at >= six_months_ago
                    )
                ).group_by(func.date_trunc('month', Application.applied_at)).order_by('month')
            else:
                # For recruiters, get applications to their company's jobs
                query = select(
                    func.date_trunc('month', Application.applied_at).label('month'),
                    func.count(Application.id).label('count')
                ).join(Job).join(User, Job.recruiter_id == User.id).where(
                    and_(
                        User.id == user_id,
                        Application.applied_at >= six_months_ago
                    )
                ).group_by(func.date_trunc('month', Application.applied_at)).order_by('month')
            
            result = await db.execute(query)
            trends = []
            
            for row in result:
                trends.append({
                    'month': row.month.strftime('%Y-%m') if row.month else '',
                    'count': row.count
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting application trends: {e}")
            return []

    async def _get_hiring_metrics(self, db: AsyncSession, company_id: int) -> Dict[str, Any]:
        """Get hiring metrics for a company"""
        try:
            metrics = {}
            
            # Time to hire (average days from application to acceptance)
            time_to_hire_query = text("""
                SELECT AVG(
                    EXTRACT(EPOCH FROM (updated_at - applied_at)) / 86400
                ) as avg_days
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE j.company_id = :company_id 
                AND a.status = 'accepted'
                AND a.updated_at IS NOT NULL
            """)
            
            result = await db.execute(time_to_hire_query, {'company_id': company_id})
            avg_days = result.scalar()
            metrics['average_time_to_hire'] = round(avg_days, 1) if avg_days else None
            
            # Conversion rates
            total_apps_query = select(func.count(Application.id)).join(Job).where(Job.company_id == company_id)
            result = await db.execute(total_apps_query)
            total_applications = result.scalar() or 0
            
            if total_applications > 0:
                # Interview rate
                interview_query = select(func.count(Application.id)).join(Job).where(
                    and_(
                        Job.company_id == company_id,
                        Application.status.in_(['interview_scheduled', 'interviewed', 'accepted'])
                    )
                )
                result = await db.execute(interview_query)
                interviews = result.scalar() or 0
                metrics['interview_rate'] = round((interviews / total_applications) * 100, 1)
                
                # Hire rate
                hire_query = select(func.count(Application.id)).join(Job).where(
                    and_(Job.company_id == company_id, Application.status == 'accepted')
                )
                result = await db.execute(hire_query)
                hires = result.scalar() or 0
                metrics['hire_rate'] = round((hires / total_applications) * 100, 1)
            else:
                metrics['interview_rate'] = 0
                metrics['hire_rate'] = 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting hiring metrics: {e}")
            return {}

    async def _get_top_performing_jobs(self, db: AsyncSession, company_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing jobs by application count"""
        try:
            query = select(
                Job.id,
                Job.title,
                func.count(Application.id).label('application_count'),
                Job.created_at
            ).outerjoin(Application).where(
                Job.company_id == company_id
            ).group_by(Job.id, Job.title, Job.created_at).order_by(
                desc('application_count')
            ).limit(limit)
            
            result = await db.execute(query)
            jobs = []
            
            for row in result:
                jobs.append({
                    'job_id': row.id,
                    'title': row.title,
                    'application_count': row.application_count,
                    'posted_date': row.created_at.strftime('%Y-%m-%d') if row.created_at else ''
                })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting top performing jobs: {e}")
            return []

    async def _get_platform_growth_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get platform growth metrics"""
        try:
            metrics = {}
            
            # User growth (last 12 months)
            twelve_months_ago = datetime.utcnow() - timedelta(days=365)
            
            user_growth_query = select(
                func.date_trunc('month', User.created_at).label('month'),
                func.count(User.id).label('count')
            ).where(
                User.created_at >= twelve_months_ago
            ).group_by(func.date_trunc('month', User.created_at)).order_by('month')
            
            result = await db.execute(user_growth_query)
            user_growth = []
            
            for row in result:
                user_growth.append({
                    'month': row.month.strftime('%Y-%m') if row.month else '',
                    'count': row.count
                })
            
            metrics['user_growth'] = user_growth
            
            # Job posting trends
            job_growth_query = select(
                func.date_trunc('month', Job.created_at).label('month'),
                func.count(Job.id).label('count')
            ).where(
                Job.created_at >= twelve_months_ago
            ).group_by(func.date_trunc('month', Job.created_at)).order_by('month')
            
            result = await db.execute(job_growth_query)
            job_growth = []
            
            for row in result:
                job_growth.append({
                    'month': row.month.strftime('%Y-%m') if row.month else '',
                    'count': row.count
                })
            
            metrics['job_growth'] = job_growth
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting platform growth metrics: {e}")
            return {}

    async def _get_popular_job_categories(self, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular job categories"""
        try:
            # This is a simplified version - in production, you'd have a proper job category system
            query = select(
                Job.job_type,
                func.count(Job.id).label('count')
            ).where(
                Job.status == 'published'
            ).group_by(Job.job_type).order_by(desc('count')).limit(limit)
            
            result = await db.execute(query)
            categories = []
            
            for row in result:
                categories.append({
                    'category': row.job_type,
                    'count': row.count
                })
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting popular job categories: {e}")
            return []

    async def get_job_analytics(self, db: AsyncSession, job_id: int) -> Dict[str, Any]:
        """Get detailed analytics for a specific job"""
        try:
            analytics = {}
            
            # Basic stats
            job_query = select(Job).where(Job.id == job_id)
            result = await db.execute(job_query)
            job = result.scalar_one_or_none()
            
            if not job:
                return {'error': 'Job not found'}
            
            # Application count
            app_count_query = select(func.count(Application.id)).where(Application.job_id == job_id)
            result = await db.execute(app_count_query)
            analytics['total_applications'] = result.scalar() or 0
            
            # Applications by status
            status_query = select(
                Application.status,
                func.count(Application.id).label('count')
            ).where(Application.job_id == job_id).group_by(Application.status)
            
            result = await db.execute(status_query)
            analytics['applications_by_status'] = {row.status: row.count for row in result}
            
            # Application timeline (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            timeline_query = select(
                func.date_trunc('day', Application.applied_at).label('date'),
                func.count(Application.id).label('count')
            ).where(
                and_(
                    Application.job_id == job_id,
                    Application.applied_at >= thirty_days_ago
                )
            ).group_by(func.date_trunc('day', Application.applied_at)).order_by('date')
            
            result = await db.execute(timeline_query)
            timeline = []
            
            for row in result:
                timeline.append({
                    'date': row.date.strftime('%Y-%m-%d') if row.date else '',
                    'applications': row.count
                })
            
            analytics['application_timeline'] = timeline
            
            # Top skills from applicants (if available)
            # This would require storing parsed resume data
            analytics['top_applicant_skills'] = []
            
            # Conversion funnel
            total_apps = analytics['total_applications']
            if total_apps > 0:
                status_counts = analytics['applications_by_status']
                
                funnel = {
                    'applied': total_apps,
                    'under_review': status_counts.get('under_review', 0),
                    'shortlisted': status_counts.get('shortlisted', 0),
                    'interviewed': status_counts.get('interviewed', 0),
                    'accepted': status_counts.get('accepted', 0)
                }
                
                analytics['conversion_funnel'] = funnel
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting job analytics: {e}")
            return {'error': str(e)}

    async def get_application_analytics(self, db: AsyncSession, company_id: Optional[int] = None) -> Dict[str, Any]:
        """Get application analytics for a company or platform-wide"""
        try:
            analytics = {}
            
            # Base query
            base_query = select(Application)
            if company_id:
                base_query = base_query.join(Job).where(Job.company_id == company_id)
            
            # Total applications
            count_query = select(func.count(Application.id))
            if company_id:
                count_query = count_query.select_from(Application).join(Job).where(Job.company_id == company_id)
            
            result = await db.execute(count_query)
            analytics['total_applications'] = result.scalar() or 0
            
            # Applications by status
            status_query = select(
                Application.status,
                func.count(Application.id).label('count')
            )
            if company_id:
                status_query = status_query.join(Job).where(Job.company_id == company_id)
            
            status_query = status_query.group_by(Application.status)
            
            result = await db.execute(status_query)
            analytics['applications_by_status'] = {row.status: row.count for row in result}
            
            # Monthly trends (last 12 months)
            twelve_months_ago = datetime.utcnow() - timedelta(days=365)
            
            trend_query = select(
                func.date_trunc('month', Application.applied_at).label('month'),
                func.count(Application.id).label('count')
            ).where(Application.applied_at >= twelve_months_ago)
            
            if company_id:
                trend_query = trend_query.join(Job).where(Job.company_id == company_id)
            
            trend_query = trend_query.group_by(func.date_trunc('month', Application.applied_at)).order_by('month')
            
            result = await db.execute(trend_query)
            monthly_trends = []
            
            for row in result:
                monthly_trends.append({
                    'month': row.month.strftime('%Y-%m') if row.month else '',
                    'applications': row.count
                })
            
            analytics['monthly_trends'] = monthly_trends
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting application analytics: {e}")
            return {'error': str(e)}


# Global analytics service instance
analytics_service = AnalyticsService()