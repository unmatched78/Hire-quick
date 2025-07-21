"""
Email Service

Email notifications and communication service.
"""

import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications and communications"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@hirequick.com')
        
        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        template_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Create default templates if they don't exist
        self._create_default_templates()

    def _create_default_templates(self):
        """Create default email templates"""
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        
        templates = {
            "welcome.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Hire Quick</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .button { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Hire Quick!</h1>
        </div>
        <div class="content">
            <h2>Hello {{ name }}!</h2>
            <p>Welcome to Hire Quick, the modern recruitment platform. We're excited to have you on board!</p>
            
            {% if user_type == 'candidate' %}
            <p>As a candidate, you can:</p>
            <ul>
                <li>Search and apply for jobs</li>
                <li>Get AI-powered job recommendations</li>
                <li>Track your applications</li>
                <li>Prepare for interviews with our AI interviewer</li>
            </ul>
            {% else %}
            <p>As a recruiter, you can:</p>
            <ul>
                <li>Post and manage job listings</li>
                <li>Review applications with AI assistance</li>
                <li>Schedule interviews</li>
                <li>Access analytics and insights</li>
            </ul>
            {% endif %}
            
            {% if verification_link %}
            <p>Please verify your email address to get started:</p>
            <p><a href="{{ verification_link }}" class="button">Verify Email</a></p>
            {% endif %}
            
            <p>Best regards,<br>The Hire Quick Team</p>
        </div>
    </div>
</body>
</html>
            """,
            
            "application_received.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Application Received</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #28a745; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Received</h1>
        </div>
        <div class="content">
            <h2>Hello {{ candidate_name }}!</h2>
            <p>Thank you for applying to the <strong>{{ job_title }}</strong> position at <strong>{{ company_name }}</strong>.</p>
            
            <p><strong>Application Details:</strong></p>
            <ul>
                <li>Position: {{ job_title }}</li>
                <li>Company: {{ company_name }}</li>
                <li>Applied on: {{ applied_date }}</li>
                <li>Application ID: #{{ application_id }}</li>
            </ul>
            
            <p>Your application is now under review. We'll keep you updated on the status of your application.</p>
            
            <p>Best regards,<br>{{ company_name }} Recruitment Team</p>
        </div>
    </div>
</body>
</html>
            """,
            
            "interview_scheduled.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Interview Scheduled</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #17a2b8; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .interview-details { background: white; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Interview Scheduled</h1>
        </div>
        <div class="content">
            <h2>Hello {{ candidate_name }}!</h2>
            <p>Great news! We'd like to invite you for an interview for the <strong>{{ job_title }}</strong> position.</p>
            
            <div class="interview-details">
                <h3>Interview Details:</h3>
                <ul>
                    <li><strong>Position:</strong> {{ job_title }}</li>
                    <li><strong>Company:</strong> {{ company_name }}</li>
                    <li><strong>Date & Time:</strong> {{ interview_date }}</li>
                    <li><strong>Type:</strong> {{ interview_type }}</li>
                    {% if interview_location %}
                    <li><strong>Location:</strong> {{ interview_location }}</li>
                    {% endif %}
                    {% if meeting_link %}
                    <li><strong>Meeting Link:</strong> <a href="{{ meeting_link }}">{{ meeting_link }}</a></li>
                    {% endif %}
                    <li><strong>Duration:</strong> {{ duration }} minutes</li>
                </ul>
            </div>
            
            {% if interview_notes %}
            <p><strong>Additional Notes:</strong></p>
            <p>{{ interview_notes }}</p>
            {% endif %}
            
            <p>Please confirm your attendance by replying to this email.</p>
            
            <p>Best regards,<br>{{ company_name }} Recruitment Team</p>
        </div>
    </div>
</body>
</html>
            """,
            
            "application_status_update.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Application Status Update</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #6c757d; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .status-accepted { color: #28a745; font-weight: bold; }
        .status-rejected { color: #dc3545; font-weight: bold; }
        .status-shortlisted { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Status Update</h1>
        </div>
        <div class="content">
            <h2>Hello {{ candidate_name }}!</h2>
            <p>We have an update regarding your application for the <strong>{{ job_title }}</strong> position at <strong>{{ company_name }}</strong>.</p>
            
            <p>Your application status has been updated to: <span class="status-{{ status|lower }}">{{ status|title }}</span></p>
            
            {% if status == 'shortlisted' %}
            <p>Congratulations! You've been shortlisted for this position. We'll be in touch soon with next steps.</p>
            {% elif status == 'accepted' %}
            <p>Congratulations! We're pleased to offer you the position. Our HR team will contact you with details.</p>
            {% elif status == 'rejected' %}
            <p>Thank you for your interest in this position. While we won't be moving forward with your application at this time, we encourage you to apply for other opportunities that match your skills.</p>
            {% endif %}
            
            {% if notes %}
            <p><strong>Additional Notes:</strong></p>
            <p>{{ notes }}</p>
            {% endif %}
            
            <p>Best regards,<br>{{ company_name }} Recruitment Team</p>
        </div>
    </div>
</body>
</html>
            """
        }
        
        for filename, content in templates.items():
            template_path = template_dir / filename
            if not template_path.exists():
                template_path.write_text(content.strip())

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content (optional)
            attachments: List of attachments (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Send email using aiosmtplib for async support
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            with open(attachment['path'], 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                message.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment['filename']}: {e}")

    async def send_welcome_email(self, user_data: Dict[str, Any]) -> bool:
        """Send welcome email to new user"""
        try:
            template = self.jinja_env.get_template('welcome.html')
            html_content = template.render(**user_data)
            
            subject = "Welcome to Hire Quick!"
            
            return await self.send_email(
                to_email=user_data['email'],
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False

    async def send_application_received_email(self, application_data: Dict[str, Any]) -> bool:
        """Send application received confirmation email"""
        try:
            template = self.jinja_env.get_template('application_received.html')
            html_content = template.render(**application_data)
            
            subject = f"Application Received - {application_data['job_title']}"
            
            return await self.send_email(
                to_email=application_data['candidate_email'],
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send application received email: {e}")
            return False

    async def send_interview_scheduled_email(self, interview_data: Dict[str, Any]) -> bool:
        """Send interview scheduled email"""
        try:
            template = self.jinja_env.get_template('interview_scheduled.html')
            html_content = template.render(**interview_data)
            
            subject = f"Interview Scheduled - {interview_data['job_title']}"
            
            return await self.send_email(
                to_email=interview_data['candidate_email'],
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send interview scheduled email: {e}")
            return False

    async def send_application_status_update_email(self, status_data: Dict[str, Any]) -> bool:
        """Send application status update email"""
        try:
            template = self.jinja_env.get_template('application_status_update.html')
            html_content = template.render(**status_data)
            
            subject = f"Application Update - {status_data['job_title']}"
            
            return await self.send_email(
                to_email=status_data['candidate_email'],
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send status update email: {e}")
            return False

    async def send_bulk_emails(self, email_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Send bulk emails
        
        Args:
            email_list: List of email data dictionaries
            
        Returns:
            Dictionary with success and failure counts
        """
        results = {'success': 0, 'failed': 0}
        
        # Process emails in batches to avoid overwhelming the SMTP server
        batch_size = 10
        for i in range(0, len(email_list), batch_size):
            batch = email_list[i:i + batch_size]
            
            # Send batch concurrently
            tasks = []
            for email_data in batch:
                task = self.send_email(
                    to_email=email_data['to_email'],
                    subject=email_data['subject'],
                    html_content=email_data['html_content'],
                    text_content=email_data.get('text_content'),
                    attachments=email_data.get('attachments')
                )
                tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results['failed'] += 1
                elif result:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        logger.info(f"Bulk email results: {results['success']} sent, {results['failed']} failed")
        return results

    async def send_password_reset_email(self, email: str, reset_token: str, reset_url: str) -> bool:
        """Send password reset email"""
        try:
            html_content = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested a password reset for your Hire Quick account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}?token={reset_token}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <p>Best regards,<br>The Hire Quick Team</p>
            </body>
            </html>
            """
            
            return await self.send_email(
                to_email=email,
                subject="Password Reset - Hire Quick",
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False

    async def send_email_verification(self, email: str, verification_token: str, verification_url: str) -> bool:
        """Send email verification email"""
        try:
            html_content = f"""
            <html>
            <body>
                <h2>Verify Your Email Address</h2>
                <p>Thank you for signing up with Hire Quick!</p>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_url}?token={verification_token}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>Best regards,<br>The Hire Quick Team</p>
            </body>
            </html>
            """
            
            return await self.send_email(
                to_email=email,
                subject="Verify Your Email - Hire Quick",
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False


# Global email service instance
email_service = EmailService()