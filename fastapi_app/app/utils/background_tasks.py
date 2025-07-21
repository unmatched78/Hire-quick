"""
Background Tasks

Background task utilities for async processing.
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.email_service import email_service
from ..services.ai_service import ai_service

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Background task manager for handling async operations"""
    
    def __init__(self):
        self.running_tasks = {}
        self.task_queue = asyncio.Queue()
        self.workers = []
        self.is_running = False

    async def start_workers(self, num_workers: int = 3):
        """Start background workers"""
        if self.is_running:
            return
        
        self.is_running = True
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Started {num_workers} background workers")

    async def stop_workers(self):
        """Stop background workers"""
        self.is_running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Stopped all background workers")

    async def _worker(self, worker_name: str):
        """Background worker to process tasks"""
        logger.info(f"Background worker {worker_name} started")
        
        while self.is_running:
            try:
                # Get task from queue with timeout
                task_data = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                task_id = task_data['id']
                task_func = task_data['func']
                task_args = task_data.get('args', [])
                task_kwargs = task_data.get('kwargs', {})
                
                logger.info(f"Worker {worker_name} processing task {task_id}")
                
                try:
                    # Execute task
                    if asyncio.iscoroutinefunction(task_func):
                        result = await task_func(*task_args, **task_kwargs)
                    else:
                        result = task_func(*task_args, **task_kwargs)
                    
                    # Mark task as completed
                    if task_id in self.running_tasks:
                        self.running_tasks[task_id]['status'] = 'completed'
                        self.running_tasks[task_id]['result'] = result
                        self.running_tasks[task_id]['completed_at'] = datetime.utcnow()
                    
                    logger.info(f"Task {task_id} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Task {task_id} failed: {e}")
                    
                    if task_id in self.running_tasks:
                        self.running_tasks[task_id]['status'] = 'failed'
                        self.running_tasks[task_id]['error'] = str(e)
                        self.running_tasks[task_id]['completed_at'] = datetime.utcnow()
                
                finally:
                    self.task_queue.task_done()
                    
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)

    async def add_task(
        self,
        task_func: Callable,
        *args,
        task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Add a task to the background queue"""
        import uuid
        
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        task_data = {
            'id': task_id,
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'created_at': datetime.utcnow()
        }
        
        # Track task
        self.running_tasks[task_id] = {
            'status': 'queued',
            'created_at': datetime.utcnow(),
            'result': None,
            'error': None
        }
        
        # Add to queue
        await self.task_queue.put(task_data)
        
        logger.info(f"Task {task_id} added to queue")
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background task"""
        return self.running_tasks.get(task_id)

    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task_info in self.running_tasks.items():
            if (task_info['status'] in ['completed', 'failed'] and 
                task_info.get('completed_at', datetime.utcnow()) < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.running_tasks[task_id]
        
        if tasks_to_remove:
            logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")


# Global task manager
task_manager = BackgroundTaskManager()


# Specific background task functions
async def send_welcome_email_task(user_data: Dict[str, Any]):
    """Background task to send welcome email"""
    try:
        success = await email_service.send_welcome_email(user_data)
        return {'success': success}
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        raise


async def send_application_notification_task(application_data: Dict[str, Any]):
    """Background task to send application notification"""
    try:
        success = await email_service.send_application_received_email(application_data)
        return {'success': success}
    except Exception as e:
        logger.error(f"Failed to send application notification: {e}")
        raise


async def process_resume_task(resume_text: str, user_id: int):
    """Background task to process resume with AI"""
    try:
        parsed_data = await ai_service.parse_resume(resume_text)
        
        # Here you would typically save the parsed data to the database
        # For now, we'll just return it
        
        return {
            'user_id': user_id,
            'parsed_data': parsed_data,
            'processed_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to process resume: {e}")
        raise


async def generate_job_recommendations_task(user_id: int):
    """Background task to generate job recommendations"""
    try:
        async for db in get_db():
            recommendations = await ai_service.get_job_recommendations(db, user_id)
            
            # Here you would typically cache or save the recommendations
            
            return {
                'user_id': user_id,
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to generate job recommendations: {e}")
        raise


async def send_interview_reminder_task(interview_data: Dict[str, Any]):
    """Background task to send interview reminder"""
    try:
        # Send reminder email 24 hours before interview
        success = await email_service.send_interview_scheduled_email(interview_data)
        return {'success': success}
    except Exception as e:
        logger.error(f"Failed to send interview reminder: {e}")
        raise


async def analyze_application_quality_task(application_data: Dict[str, Any]):
    """Background task to analyze application quality"""
    try:
        analysis = await ai_service.analyze_application_quality(application_data)
        
        # Here you would typically save the analysis to the database
        
        return {
            'application_id': application_data.get('application_id'),
            'analysis': analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze application quality: {e}")
        raise


async def send_bulk_notifications_task(notifications: List[Dict[str, Any]]):
    """Background task to send bulk notifications"""
    try:
        results = await email_service.send_bulk_emails(notifications)
        return results
    except Exception as e:
        logger.error(f"Failed to send bulk notifications: {e}")
        raise


async def cleanup_old_files_task(days_old: int = 30):
    """Background task to clean up old files"""
    try:
        from ..utils.file_handler import file_handler
        deleted_count = await file_handler.cleanup_old_files(days_old)
        return {'deleted_files': deleted_count}
    except Exception as e:
        logger.error(f"Failed to cleanup old files: {e}")
        raise


async def generate_analytics_report_task(company_id: Optional[int] = None, report_type: str = "monthly"):
    """Background task to generate analytics report"""
    try:
        from ..services.analytics_service import analytics_service
        
        async for db in get_db():
            if report_type == "application_analytics":
                report_data = await analytics_service.get_application_analytics(db, company_id)
            else:
                # Default to dashboard stats
                user_type = "admin" if company_id is None else "recruiter"
                report_data = await analytics_service.get_dashboard_stats(db, company_id or 1, user_type)
            
            return {
                'company_id': company_id,
                'report_type': report_type,
                'data': report_data,
                'generated_at': datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {e}")
        raise


# Convenience functions for common tasks
async def schedule_welcome_email(user_data: Dict[str, Any]) -> str:
    """Schedule welcome email to be sent in background"""
    return await task_manager.add_task(send_welcome_email_task, user_data)


async def schedule_application_notification(application_data: Dict[str, Any]) -> str:
    """Schedule application notification to be sent in background"""
    return await task_manager.add_task(send_application_notification_task, application_data)


async def schedule_resume_processing(resume_text: str, user_id: int) -> str:
    """Schedule resume processing in background"""
    return await task_manager.add_task(process_resume_task, resume_text, user_id)


async def schedule_job_recommendations(user_id: int) -> str:
    """Schedule job recommendations generation in background"""
    return await task_manager.add_task(generate_job_recommendations_task, user_id)


async def schedule_interview_reminder(interview_data: Dict[str, Any], delay_hours: int = 24) -> str:
    """Schedule interview reminder to be sent after delay"""
    # For now, we'll send immediately. In production, you'd use a scheduler like Celery
    return await task_manager.add_task(send_interview_reminder_task, interview_data)


async def schedule_application_analysis(application_data: Dict[str, Any]) -> str:
    """Schedule application quality analysis in background"""
    return await task_manager.add_task(analyze_application_quality_task, application_data)


# Startup and shutdown functions
async def startup_background_tasks():
    """Start background task workers on application startup"""
    await task_manager.start_workers(num_workers=3)


async def shutdown_background_tasks():
    """Stop background task workers on application shutdown"""
    await task_manager.stop_workers()