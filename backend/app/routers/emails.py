from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from ..services.email_service import get_email_service
from pydantic import BaseModel

router = APIRouter(prefix="/emails", tags=["emails"])


class InterviewEmailRequest(BaseModel):
    """Request to send interview email"""
    candidate_id: int
    job_id: int
    interview_date: Optional[str] = None
    interview_time: Optional[str] = None
    interview_location: Optional[str] = None


class RejectionEmailRequest(BaseModel):
    """Request to send rejection email"""
    candidate_id: int
    job_id: int


class EmailResponse(BaseModel):
    """Response from email sending"""
    success: bool
    message: str
    email_log_id: Optional[int] = None


@router.post("/send-interview", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def send_interview_email_endpoint(
    request: InterviewEmailRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Send an interview email to a candidate."""
    # Verify candidate belongs to user's company
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == request.candidate_id,
        models.Candidate.company_id == current_user.company_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Verify job belongs to user's company
    job = db.query(models.Job).filter(
        models.Job.id == request.job_id,
        models.Job.company_id == current_user.company_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get sender email from user account
    sender_email = current_user.sender_email
    if not sender_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a sender_email configured"
        )
    
    # Check if candidate has email
    if not candidate.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate email not available"
        )
    
    # Get email service
    email_service = get_email_service()
    
    try:
        # Send email
        success = email_service.send_interview_email(
            sender_email=sender_email,
            recipient_email=candidate.email,
            candidate_name=candidate.name or "Candidate",
            job_title=job.title,
            interview_date=request.interview_date,
            interview_time=request.interview_time,
            interview_location=request.interview_location,
        )
        
        if not success:
            error_detail = email_service.get_last_error() or "Failed to send email"
            # Provide helpful error message if SMTP is not configured
            if "login" in error_detail.lower() or "authentication" in error_detail.lower():
                error_detail = "SMTP authentication failed. Please check SMTP_USERNAME and SMTP_PASSWORD in environment variables."
            elif "connection" in error_detail.lower() or "refused" in error_detail.lower():
                error_detail = "Could not connect to SMTP server. Please check SMTP_HOST and SMTP_PORT in environment variables."
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
        
        # Log email
        email_log = models.EmailLog(
            user_id=current_user.id,
            candidate_id=candidate.id,
            job_id=job.id,
            email_type="interview",
            recipient_email=candidate.email,
            subject=f"Interview Invitation - {job.title}",
            body=f"Interview email sent to {candidate.name or candidate.email}"
        )
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        
        return EmailResponse(
            success=True,
            message="Interview email sent successfully",
            email_log_id=email_log.id
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )


@router.post("/send-rejection", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def send_rejection_email_endpoint(
    request: RejectionEmailRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Send a rejection email to a candidate."""
    # Verify candidate belongs to user's company
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == request.candidate_id,
        models.Candidate.company_id == current_user.company_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Verify job belongs to user's company
    job = db.query(models.Job).filter(
        models.Job.id == request.job_id,
        models.Job.company_id == current_user.company_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get sender email from user account
    sender_email = current_user.sender_email
    if not sender_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a sender_email configured"
        )
    
    # Check if candidate has email
    if not candidate.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate email not available"
        )
    
    # Get email service
    email_service = get_email_service()
    
    try:
        # Send email
        success = email_service.send_rejection_email(
            sender_email=sender_email,
            recipient_email=candidate.email,
            candidate_name=candidate.name or "Candidate",
            job_title=job.title,
        )
        
        if not success:
            error_detail = email_service.get_last_error() or "Failed to send email"
            # Provide helpful error message if SMTP is not configured
            if "login" in error_detail.lower() or "authentication" in error_detail.lower():
                error_detail = "SMTP authentication failed. Please check SMTP_USERNAME and SMTP_PASSWORD in environment variables."
            elif "connection" in error_detail.lower() or "refused" in error_detail.lower():
                error_detail = "Could not connect to SMTP server. Please check SMTP_HOST and SMTP_PORT in environment variables."
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
        
        # Log email
        email_log = models.EmailLog(
            user_id=current_user.id,
            candidate_id=candidate.id,
            job_id=job.id,
            email_type="rejection",
            recipient_email=candidate.email,
            subject=f"Update on Your Application - {job.title}",
            body=f"Rejection email sent to {candidate.name or candidate.email}"
        )
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        
        return EmailResponse(
            success=True,
            message="Rejection email sent successfully",
            email_log_id=email_log.id
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )

