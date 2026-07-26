from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreate(BaseModel):
    title: str
    criteria_json: Dict[str, Any]  # Job criteria as JSON
    status: Optional[str] = "active"


class JobResponse(BaseModel):
    id: int
    title: str
    company_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new job for the authenticated user's company"""
    job = models.Job(
        title=job_data.title,
        company_id=current_user.company_id,
        criteria_json=job_data.criteria_json,
        status=job_data.status
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=List[JobResponse])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all jobs for the authenticated user's company"""
    jobs = db.query(models.Job).filter(
        models.Job.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific job by ID (only if belongs to user's company)"""
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.company_id == current_user.company_id
    ).first()
    
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete a job by ID (only if belongs to user's company)"""
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.company_id == current_user.company_id
    ).first()
    
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Delete related scores first
    db.query(models.CandidateScore).filter(
        models.CandidateScore.job_id == job_id
    ).delete()
    
    # Delete the job
    db.delete(job)
    db.commit()
    
    return None

