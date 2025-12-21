import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from jinja2 import Template
import os
from ..config import settings


class EmailService:
    """SMTP email service for sending interview and rejection emails"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST") or getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv("SMTP_PORT") or getattr(settings, 'SMTP_PORT', 587))
        self.smtp_username = os.getenv("SMTP_USERNAME") or getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = os.getenv("SMTP_PASSWORD") or getattr(settings, 'SMTP_PASSWORD', None)
        self.use_tls = getattr(settings, 'SMTP_USE_TLS', True)
    
    def _get_smtp_connection(self):
        """Create and return SMTP connection"""
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        if self.use_tls:
            server.starttls()
        if self.smtp_username and self.smtp_password:
            server.login(self.smtp_username, self.smtp_password)
        return server
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render email template with variables"""
        jinja_template = Template(template)
        return jinja_template.render(**variables)
    
    def send_email(
        self,
        sender_email: str,
        recipient_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            sender_email: Email address to send from (user's sender_email)
            recipient_email: Email address to send to
            subject: Email subject
            body: Email body (plain text or HTML)
            is_html: Whether body is HTML format
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = self._get_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error sending email: {error_msg}")
            # Store error for better error reporting
            self._last_error = error_msg
            return False
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return getattr(self, '_last_error', None)
    
    def send_interview_email(
        self,
        sender_email: str,
        recipient_email: str,
        candidate_name: str,
        job_title: str,
        interview_date: Optional[str] = None,
        interview_time: Optional[str] = None,
        interview_location: Optional[str] = None,
        additional_info: Optional[str] = None,
        custom_template: Optional[str] = None
    ) -> bool:
        """
        Send interview invitation email.
        
        Args:
            sender_email: Email address to send from
            recipient_email: Candidate email address
            candidate_name: Candidate's name
            job_title: Job position title
            interview_date: Interview date (optional)
            interview_time: Interview time (optional)
            interview_location: Interview location (optional)
            additional_info: Additional information (optional)
            custom_template: Custom email template (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        # Default interview email template
        default_template = """Dear {{ candidate_name }},

Congratulations! We are pleased to invite you for an interview for the {{ job_title }} position.

{% if interview_date %}
Interview Date: {{ interview_date }}
{% endif %}
{% if interview_time %}
Interview Time: {{ interview_time }}
{% endif %}
{% if interview_location %}
Location: {{ interview_location }}
{% endif %}

{% if additional_info %}
{{ additional_info }}
{% endif %}

We look forward to meeting you!

Best regards,
Recruitment Team"""
        
        template = custom_template or default_template
        
        variables = {
            'candidate_name': candidate_name,
            'job_title': job_title,
            'interview_date': interview_date,
            'interview_time': interview_time,
            'interview_location': interview_location,
            'additional_info': additional_info,
        }
        
        body = self._render_template(template, variables)
        subject = f"Interview Invitation - {job_title}"
        
        return self.send_email(
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            is_html=False
        )
    
    def send_rejection_email(
        self,
        sender_email: str,
        recipient_email: str,
        candidate_name: str,
        job_title: str,
        feedback: Optional[str] = None,
        custom_template: Optional[str] = None
    ) -> bool:
        """
        Send rejection email.
        
        Args:
            sender_email: Email address to send from
            recipient_email: Candidate email address
            candidate_name: Candidate's name
            job_title: Job position title
            feedback: Optional feedback message (optional)
            custom_template: Custom email template (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        # Default rejection email template
        default_template = """Dear {{ candidate_name }},

Thank you for your interest in the {{ job_title }} position and for taking the time to interview with us.

After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current needs.

{% if feedback %}
{{ feedback }}
{% endif %}

We appreciate your interest in our company and wish you the best in your job search.

Best regards,
Recruitment Team"""
        
        template = custom_template or default_template
        
        variables = {
            'candidate_name': candidate_name,
            'job_title': job_title,
            'feedback': feedback,
        }
        
        body = self._render_template(template, variables)
        subject = f"Update on Your Application - {job_title}"
        
        return self.send_email(
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            is_html=False
        )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

