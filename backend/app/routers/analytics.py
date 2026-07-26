from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsResponse(BaseModel):
    total_jobs: int
    total_candidates: int
    total_scores: int
    average_score: float
    score_distribution: Dict[str, int]  # {"0-20": count, "21-40": count, etc.}
    top_candidates: List[Dict[str, Any]]
    jobs_summary: List[Dict[str, Any]]
    authenticity_stats: Dict[str, int]
    category_averages: Dict[str, float]


@router.get("/", response_model=AnalyticsResponse)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get analytics and statistics for the authenticated user's company"""
    
    # Total jobs
    total_jobs = db.query(models.Job).filter(
        models.Job.company_id == current_user.company_id
    ).count()
    
    # Total candidates
    total_candidates = db.query(models.Candidate).filter(
        models.Candidate.company_id == current_user.company_id
    ).count()
    
    # Total scores
    total_scores = db.query(models.CandidateScore).join(
        models.Candidate
    ).filter(
        models.Candidate.company_id == current_user.company_id
    ).count()
    
    # Average score
    avg_score_result = db.query(func.avg(models.CandidateScore.total_score)).join(
        models.Candidate
    ).filter(
        models.Candidate.company_id == current_user.company_id,
        models.CandidateScore.total_score.isnot(None)
    ).scalar()
    
    average_score = float(avg_score_result) if avg_score_result else 0.0
    
    # Score distribution
    all_scores = db.query(models.CandidateScore.total_score).join(
        models.Candidate
    ).filter(
        models.Candidate.company_id == current_user.company_id,
        models.CandidateScore.total_score.isnot(None)
    ).all()
    
    score_distribution = {
        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-100": 0
    }
    
    for (score,) in all_scores:
        if score is not None:
            if score <= 20:
                score_distribution["0-20"] += 1
            elif score <= 40:
                score_distribution["21-40"] += 1
            elif score <= 60:
                score_distribution["41-60"] += 1
            elif score <= 80:
                score_distribution["61-80"] += 1
            else:
                score_distribution["81-100"] += 1
    
    # Top candidates (top 5 by score)
    top_candidates_query = db.query(
        models.Candidate.id,
        models.Candidate.name,
        models.CandidateScore.total_score,
        models.Job.title.label('job_title'),
        models.Job.id.label('job_id')
    ).join(
        models.CandidateScore, models.Candidate.id == models.CandidateScore.candidate_id
    ).join(
        models.Job, models.CandidateScore.job_id == models.Job.id
    ).filter(
        models.Candidate.company_id == current_user.company_id,
        models.CandidateScore.total_score.isnot(None)
    ).order_by(
        models.CandidateScore.total_score.desc()
    ).limit(5).all()
    
    top_candidates = [
        {
            "candidate_id": row.id,
            "name": row.name or "Unknown",
            "score": float(row.total_score),
            "job_title": row.job_title,
            "job_id": row.job_id
        }
        for row in top_candidates_query
    ]
    
    # Jobs summary
    jobs = db.query(models.Job).filter(
        models.Job.company_id == current_user.company_id
    ).all()
    
    jobs_summary = []
    for job in jobs:
        candidate_count = db.query(models.Candidate).filter(
            models.Candidate.company_id == current_user.company_id
        ).count()
        
        scored_count = db.query(models.CandidateScore).join(
            models.Candidate
        ).filter(
            models.CandidateScore.job_id == job.id,
            models.Candidate.company_id == current_user.company_id,
            models.CandidateScore.total_score.isnot(None)
        ).count()
        
        avg_score = db.query(func.avg(models.CandidateScore.total_score)).join(
            models.Candidate
        ).filter(
            models.CandidateScore.job_id == job.id,
            models.Candidate.company_id == current_user.company_id,
            models.CandidateScore.total_score.isnot(None)
        ).scalar()
        
        jobs_summary.append({
            "job_id": job.id,
            "title": job.title,
            "candidate_count": candidate_count,
            "scored_count": scored_count,
            "average_score": float(avg_score) if avg_score else None
        })
    
    # Authenticity stats
    suspicious_count = db.query(models.AuthenticityFlag).join(
        models.Candidate
    ).filter(
        models.Candidate.company_id == current_user.company_id,
        models.AuthenticityFlag.is_suspicious == True
    ).count()
    
    total_checked = db.query(models.AuthenticityFlag).join(
        models.Candidate
    ).filter(
        models.Candidate.company_id == current_user.company_id
    ).count()
    
    authenticity_stats = {
        "total_checked": total_checked,
        "suspicious": suspicious_count,
        "clean": total_checked - suspicious_count
    }
    
    # Category averages
    # First, get all scores for this company
    all_scores = db.query(models.CandidateScore).join(
        models.Candidate
    ).filter(
        models.Candidate.company_id == current_user.company_id
    ).all()
    
    category_totals = {}
    category_counts = {}
    
    for score in all_scores:
        category_scores = score.category_scores
        
        if isinstance(category_scores, str):
            try:
                import json
                category_scores = json.loads(category_scores)
            except (json.JSONDecodeError, TypeError):
                continue
        
        if category_scores is None or not isinstance(category_scores, dict) or len(category_scores) == 0:
            continue
        
        for category, value in category_scores.items():
            if value is None:
                continue
            
            numeric_value = None
            if isinstance(value, (int, float)):
                numeric_value = float(value)
            elif isinstance(value, dict):
                if 'score' in value and isinstance(value['score'], (int, float)):
                    numeric_value = float(value['score'])
                else:
                    for k, v in value.items():
                        if isinstance(v, (int, float)):
                            numeric_value = float(v)
                            break
            
            if numeric_value is not None and 0 <= numeric_value <= 100:
                category_totals[category] = category_totals.get(category, 0) + numeric_value
                category_counts[category] = category_counts.get(category, 0) + 1
    
    category_averages = {
        category: round(category_totals[category] / category_counts[category], 2) if category_counts[category] > 0 else 0.0
        for category in category_totals.keys()
    }
    
    return AnalyticsResponse(
        total_jobs=total_jobs,
        total_candidates=total_candidates,
        total_scores=total_scores,
        average_score=round(average_score, 2),
        score_distribution=score_distribution,
        top_candidates=top_candidates,
        jobs_summary=jobs_summary,
        authenticity_stats=authenticity_stats,
        category_averages=category_averages
    )

