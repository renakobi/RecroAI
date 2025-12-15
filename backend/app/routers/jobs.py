from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobResponse(BaseModel):
    id: int
    title: str
    company_id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


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

