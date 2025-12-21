from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from ..schemas import (
    ScoringRequest,
    ScoringResultResponse,
    CategoryScoreSchema,
    BulkScoringRequest,
    BulkScoringResponse,
    CandidateWithScore,
)

from ..services.scoring_service import score_candidate
from ..services.authenticity_service import detect_authenticity


router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.get("/candidates/{job_id}", response_model=BulkScoringResponse)
def get_candidates_with_scores(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """Get candidates with existing scores for a job (NO scoring, just fetch from DB)"""
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.company_id == current_user.company_id,
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db.query(models.Candidate).filter(
        models.Candidate.company_id == current_user.company_id
    ).all()

    if not candidates:
        return BulkScoringResponse(
            message="No candidates found",
            job_id=job_id,
            candidates_scored=0,
            candidates_checked=0,
            candidates=[],
        )

    results = []
    checked = 0

    for candidate in candidates:
        candidate_data = {
            "candidate_id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "raw_profile": candidate.raw_profile,
        }

        # Get existing authenticity flag (no LLM call)
        existing_flag = db.query(models.AuthenticityFlag).filter(
            models.AuthenticityFlag.candidate_id == candidate.id
        ).first()
        
        if existing_flag:
            candidate_data["is_suspicious"] = existing_flag.is_suspicious
            candidate_data["risk_score"] = existing_flag.risk_score
            candidate_data["flag_id"] = existing_flag.id
            checked += 1
        else:
            candidate_data["is_suspicious"] = None
            candidate_data["risk_score"] = None
            candidate_data["flag_id"] = None

        # Get existing score (no LLM call)
        existing_score = db.query(models.CandidateScore).filter(
            models.CandidateScore.candidate_id == candidate.id,
            models.CandidateScore.job_id == job.id,
        ).first()

        if existing_score and existing_score.total_score is not None:
            candidate_data["total_score"] = float(existing_score.total_score)
            if existing_score.category_scores:
                candidate_data["category_scores"] = {
                    k: CategoryScoreSchema(
                        score=float(v) if isinstance(v, (int, float)) else float(v.get("score", 0)) if isinstance(v, dict) else 0,
                        reasoning=""
                    )
                    for k, v in existing_score.category_scores.items()
                }
            else:
                candidate_data["category_scores"] = None
            candidate_data["score_id"] = existing_score.id
            candidate_data["explanation"] = existing_score.explanation
        else:
            candidate_data["total_score"] = None
            candidate_data["category_scores"] = None
            candidate_data["score_id"] = None
            candidate_data["explanation"] = None

        results.append(CandidateWithScore(**candidate_data))

    results.sort(key=lambda c: c.total_score or 0, reverse=True)

    scored_count = sum(1 for r in results if r.total_score is not None)
    
    return BulkScoringResponse(
        message=f"Retrieved {len(candidates)} candidates ({scored_count} with scores)",
        job_id=job.id,
        candidates_scored=scored_count,
        candidates_checked=checked,
        candidates=results,
    )


@router.post("/score", response_model=ScoringResultResponse, status_code=status.HTTP_201_CREATED)
async def score_single_candidate(
    request: ScoringRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    # Verify candidate
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == request.candidate_id,
        models.Candidate.company_id == current_user.company_id,
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Verify job
    job = db.query(models.Job).filter(
        models.Job.id == request.job_id,
        models.Job.company_id == current_user.company_id,
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Prevent duplicate scoring
    if db.query(models.CandidateScore).filter(
        models.CandidateScore.candidate_id == request.candidate_id,
        models.CandidateScore.job_id == request.job_id,
    ).first():
        raise HTTPException(status_code=400, detail="Score already exists")

    # Parse job criteria
    job_criteria = job.criteria_json if isinstance(job.criteria_json, dict) else json.loads(job.criteria_json)
    
    # Parse candidate profile
    if isinstance(candidate.raw_profile, str):
        try:
            candidate_profile_data = json.loads(candidate.raw_profile)
            candidate_profile = json.dumps(candidate_profile_data, indent=2)
        except json.JSONDecodeError:
            candidate_profile = candidate.raw_profile
    else:
        candidate_profile = json.dumps(candidate.raw_profile, indent=2)

    try:
        # Synchronous call - no await (OpenAI SDK is synchronous)
        result = score_candidate(
            job_criteria=job_criteria,
            candidate_profile=candidate_profile,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")

    score = models.CandidateScore(
        candidate_id=candidate.id,
        job_id=job.id,
        total_score=result["total_score"],
        category_scores=result["category_scores"],
        explanation=result["explanation"],
    )

    db.add(score)
    db.commit()
    db.refresh(score)

    return ScoringResultResponse(
        message="Candidate scored successfully",
        score_id=score.id,
        total_score=score.total_score,
        category_scores={
            k: CategoryScoreSchema(score=v, reasoning="")
            for k, v in score.category_scores.items()
        },
        explanation=score.explanation,
    )


@router.post("/score-all", response_model=BulkScoringResponse)
async def score_all_candidates_for_job(
    request: BulkScoringRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    job = db.query(models.Job).filter(
        models.Job.id == request.job_id,
        models.Job.company_id == current_user.company_id,
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates = db.query(models.Candidate).filter(
        models.Candidate.company_id == current_user.company_id
    ).all()

    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")
    
    # Safety limit: Don't score more than 4 candidates at once to prevent excessive token usage
    MAX_CANDIDATES_TO_SCORE = 4
    if len(candidates) > MAX_CANDIDATES_TO_SCORE:
        raise HTTPException(
            status_code=400, 
            detail=f"Too many candidates ({len(candidates)}). Maximum {MAX_CANDIDATES_TO_SCORE} candidates can be scored at once. Please filter your candidates first."
        )

    job_criteria = job.criteria_json if isinstance(job.criteria_json, dict) else json.loads(job.criteria_json)

    results = []
    scored = 0
    checked = 0
    errors = []
    total_candidates = len(candidates)

    for idx, candidate in enumerate(candidates, 1):
        candidate_data = {
            "candidate_id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "raw_profile": candidate.raw_profile,  # Include for filtering
        }

        # Check authenticity
        try:
            profile_text = candidate.raw_profile
            if isinstance(profile_text, str):
                text_to_analyze = profile_text
            else:
                text_to_analyze = json.dumps(profile_text, indent=2)
            
            try:
                auth = detect_authenticity(text_to_analyze, use_llm=True)
            except ValueError:
                # LLM not configured, use heuristic only
                auth = detect_authenticity(text_to_analyze, use_llm=False)
            
            # Create/update authenticity flag
            existing_flag = db.query(models.AuthenticityFlag).filter(
                models.AuthenticityFlag.candidate_id == candidate.id
            ).first()
            
            if existing_flag:
                existing_flag.is_suspicious = auth["is_suspicious"]
                existing_flag.risk_score = auth["risk_score"]
                existing_flag.reason = auth["reason"]
                flag_id = existing_flag.id
            else:
                new_flag = models.AuthenticityFlag(
                    candidate_id=candidate.id,
                    is_suspicious=auth["is_suspicious"],
                    risk_score=auth["risk_score"],
                    reason=auth["reason"]
                )
                db.add(new_flag)
                db.flush()
                flag_id = new_flag.id
            
            candidate_data["is_suspicious"] = auth["is_suspicious"]
            candidate_data["risk_score"] = auth["risk_score"]
            candidate_data["flag_id"] = flag_id
            checked += 1
        except Exception as e:
            errors.append(f"Authenticity check failed for candidate {candidate.id}: {str(e)}")
            candidate_data["is_suspicious"] = None
            candidate_data["risk_score"] = None
            candidate_data["flag_id"] = None

        # Score candidate
        existing_score = db.query(models.CandidateScore).filter(
            models.CandidateScore.candidate_id == candidate.id,
            models.CandidateScore.job_id == job.id,
        ).first()

        if existing_score and existing_score.total_score is not None:
            # Use existing score - NO LLM CALL
            score = existing_score
        else:
            # Only score if no valid score exists
            if existing_score and existing_score.total_score is None:
                db.delete(existing_score)
                db.flush()
        
        if not existing_score or existing_score.total_score is None:
            try:
                # Parse candidate profile for scoring
                if isinstance(candidate.raw_profile, str):
                    try:
                        candidate_profile_data = json.loads(candidate.raw_profile)
                        candidate_profile = json.dumps(candidate_profile_data, indent=2)
                    except json.JSONDecodeError:
                        candidate_profile = candidate.raw_profile
                else:
                    candidate_profile = json.dumps(candidate.raw_profile, indent=2)
                
                try:
                    result = score_candidate(job_criteria, candidate_profile)
                except Exception as llm_error:
                    raise
                
                score = models.CandidateScore(
                    candidate_id=candidate.id,
                    job_id=job.id,
                    total_score=float(result["total_score"]),
                    category_scores=result.get("category_scores", {}),
                    explanation=result.get("explanation", ""),
                )
                db.add(score)
                db.flush()
                
                db.refresh(score)
                scored += 1
            except ValueError as e:
                # LLM configuration error
                error_msg = f"LLM not configured for candidate {candidate.id}: {str(e)}"
                errors.append(error_msg)
                candidate_data["total_score"] = None
                candidate_data["category_scores"] = None
                candidate_data["score_id"] = None
                candidate_data["explanation"] = None
                results.append(CandidateWithScore(**candidate_data))
                continue
            except Exception as e:
                # Other scoring errors
                error_msg = f"Scoring failed for candidate {candidate.id}: {str(e)}"
                errors.append(error_msg)
                candidate_data["total_score"] = None
                candidate_data["category_scores"] = None
                candidate_data["score_id"] = None
                candidate_data["explanation"] = None
                results.append(CandidateWithScore(**candidate_data))
                continue

        candidate_data["total_score"] = float(score.total_score) if score.total_score is not None else None
        # Convert category_scores to CategoryScoreSchema format
        if score.category_scores:
            candidate_data["category_scores"] = {
                k: CategoryScoreSchema(
                    score=float(v) if isinstance(v, (int, float)) else float(v.get("score", 0)) if isinstance(v, dict) else 0,
                    reasoning=""
                )
                for k, v in score.category_scores.items()
            }
        else:
            candidate_data["category_scores"] = None
        candidate_data["score_id"] = score.id
        candidate_data["explanation"] = score.explanation

        results.append(CandidateWithScore(**candidate_data))

    db.commit()

    results.sort(key=lambda c: c.total_score or 0, reverse=True)

    message = f"Processed {len(candidates)} candidates | Scored {scored} new | Checked {checked} authenticity"
    if errors:
        message += f" | {len(errors)} errors occurred"

    # Log summary for debugging
    
    response = BulkScoringResponse(
        message=message,
        job_id=job.id,
        candidates_scored=scored,
        candidates_checked=checked,
        candidates=results,
    )
    
    return response


@router.delete("/score/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete a candidate score by ID (only if belongs to user's company)"""
    score = db.query(models.CandidateScore).join(
        models.Candidate
    ).filter(
        models.CandidateScore.id == score_id,
        models.Candidate.company_id == current_user.company_id
    ).first()
    
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    
    db.delete(score)
    db.commit()
    
    return None
