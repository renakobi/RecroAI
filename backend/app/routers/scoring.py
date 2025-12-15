from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from ..schemas import (
    ScoringRequest, ScoringResultResponse, CategoryScoreSchema,
    BulkScoringRequest, BulkScoringResponse, CandidateWithScore
)
from ..services.scoring_service import get_scoring_service
from ..services.authenticity_service import get_authenticity_service
import json

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/score", response_model=ScoringResultResponse, status_code=status.HTTP_201_CREATED)
async def score_candidate(
    request: ScoringRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Score a candidate against a job using LLM.
    
    Returns structured scores and explanation. All output is validated JSON.
    """
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
    
    # Check if score already exists
    existing_score = db.query(models.CandidateScore).filter(
        models.CandidateScore.candidate_id == request.candidate_id,
        models.CandidateScore.job_id == request.job_id
    ).first()
    
    if existing_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score already exists for this candidate-job pair"
        )
    
    try:
        # Get scoring service
        scoring_service = get_scoring_service()
        
        # Parse job criteria JSON
        if isinstance(job.criteria_json, str):
            job_criteria = json.loads(job.criteria_json)
        else:
            job_criteria = job.criteria_json
        
        # Parse candidate raw profile
        if isinstance(candidate.raw_profile, str):
            try:
                candidate_profile_data = json.loads(candidate.raw_profile)
                # Convert back to readable string for LLM
                candidate_profile = json.dumps(candidate_profile_data, indent=2)
            except json.JSONDecodeError:
                # If not JSON, use as-is
                candidate_profile = candidate.raw_profile
        else:
            candidate_profile = json.dumps(candidate.raw_profile, indent=2)
        
        # Get LLM scoring (structured JSON only)
        scoring_result = await scoring_service.score_candidate(
            job_criteria=job_criteria,
            candidate_profile=candidate_profile
        )
        
        # Convert category scores to dict format for storage
        category_scores_dict = {
            category: {
                "score": score.score,
                "reasoning": score.reasoning
            }
            for category, score in scoring_result.category_scores.items()
        }
        
        # Create explanation combining explanation, strengths, and weaknesses
        explanation_parts = [scoring_result.explanation]
        if scoring_result.strengths:
            explanation_parts.append(f"\n\nStrengths: {', '.join(scoring_result.strengths)}")
        if scoring_result.weaknesses:
            explanation_parts.append(f"\n\nWeaknesses: {', '.join(scoring_result.weaknesses)}")
        full_explanation = "\n".join(explanation_parts)
        
        # Save score to database
        candidate_score = models.CandidateScore(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            total_score=scoring_result.total_score,
            category_scores=category_scores_dict,
            explanation=full_explanation
        )
        
        db.add(candidate_score)
        db.commit()
        db.refresh(candidate_score)
        
        # Return structured response
        return ScoringResultResponse(
            message="Candidate scored successfully",
            score_id=candidate_score.id,
            total_score=candidate_score.total_score,
            category_scores={
                cat: CategoryScoreSchema(**score_data)
                for cat, score_data in candidate_score.category_scores.items()
            },
            explanation=candidate_score.explanation
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scoring error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during scoring: {str(e)}"
        )


@router.get("/candidate/{candidate_id}/job/{job_id}")
def get_score(
    candidate_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get existing score for a candidate-job pair"""
    score = db.query(models.CandidateScore).filter(
        models.CandidateScore.candidate_id == candidate_id,
        models.CandidateScore.job_id == job_id
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    
    # Verify access
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id,
        models.Candidate.company_id == current_user.company_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
        return ScoringResultResponse(
            message="Score retrieved successfully",
            score_id=score.id,
            total_score=score.total_score,
            category_scores={
                cat: CategoryScoreSchema(**score_data)
                for cat, score_data in score.category_scores.items()
            },
            explanation=score.explanation
        )


@router.post("/score-all", response_model=BulkScoringResponse, status_code=status.HTTP_200_OK)
async def score_all_candidates_for_job(
    request: BulkScoringRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Score all candidates for a specific job.
    
    - Scores all candidates belonging to the job's company
    - Checks authenticity for each candidate
    - Stores scores and authenticity flags
    - Returns candidates sorted by total_score (descending)
    """
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
    
    # Get all candidates for the company
    candidates = db.query(models.Candidate).filter(
        models.Candidate.company_id == current_user.company_id
    ).all()
    
    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidates found for this company"
        )
    
    # Parse job criteria JSON
    if isinstance(job.criteria_json, str):
        job_criteria = json.loads(job.criteria_json)
    else:
        job_criteria = job.criteria_json
    
    # Get services
    scoring_service = get_scoring_service()
    authenticity_service = get_authenticity_service()
    
    candidates_with_scores = []
    candidates_scored = 0
    candidates_checked = 0
    errors = []
    
    try:
        for candidate in candidates:
            candidate_data = {
                "candidate_id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
            }
            
            # Check authenticity for each candidate
            try:
                # Parse candidate raw profile
                if isinstance(candidate.raw_profile, str):
                    text_to_analyze = candidate.raw_profile
                else:
                    text_to_analyze = json.dumps(candidate.raw_profile, indent=2)
                
                # Run authenticity check
                authenticity_result = await authenticity_service.analyze_text(
                    text_to_analyze, use_llm=True
                )
                
                # Check if flag already exists
                existing_flag = db.query(models.AuthenticityFlag).filter(
                    models.AuthenticityFlag.candidate_id == candidate.id
                ).first()
                
                if existing_flag:
                    # Update existing flag
                    existing_flag.is_suspicious = authenticity_result.is_suspicious
                    existing_flag.risk_score = authenticity_result.risk_score
                    existing_flag.reason = authenticity_result.reason
                    flag_id = existing_flag.id
                else:
                    # Create new flag
                    new_flag = models.AuthenticityFlag(
                        candidate_id=candidate.id,
                        is_suspicious=authenticity_result.is_suspicious,
                        risk_score=authenticity_result.risk_score,
                        reason=authenticity_result.reason
                    )
                    db.add(new_flag)
                    db.flush()
                    flag_id = new_flag.id
                
                candidate_data["is_suspicious"] = authenticity_result.is_suspicious
                candidate_data["risk_score"] = authenticity_result.risk_score
                candidate_data["flag_id"] = flag_id
                candidates_checked += 1
                
            except Exception as e:
                errors.append(f"Authenticity check failed for candidate {candidate.id}: {str(e)}")
                candidate_data["is_suspicious"] = None
                candidate_data["risk_score"] = None
                candidate_data["flag_id"] = None
            
            # Score candidate (skip if already scored)
            existing_score = db.query(models.CandidateScore).filter(
                models.CandidateScore.candidate_id == candidate.id,
                models.CandidateScore.job_id == request.job_id
            ).first()
            
            if existing_score:
                # Use existing score
                candidate_data["total_score"] = existing_score.total_score
                candidate_data["category_scores"] = {
                    cat: CategoryScoreSchema(**score_data)
                    for cat, score_data in existing_score.category_scores.items()
                }
                candidate_data["score_id"] = existing_score.id
            else:
                # Score candidate
                try:
                    # Parse candidate raw profile for scoring
                    if isinstance(candidate.raw_profile, str):
                        try:
                            candidate_profile_data = json.loads(candidate.raw_profile)
                            candidate_profile = json.dumps(candidate_profile_data, indent=2)
                        except json.JSONDecodeError:
                            candidate_profile = candidate.raw_profile
                    else:
                        candidate_profile = json.dumps(candidate.raw_profile, indent=2)
                    
                    # Get LLM scoring
                    scoring_result = await scoring_service.score_candidate(
                        job_criteria=job_criteria,
                        candidate_profile=candidate_profile
                    )
                    
                    # Convert category scores to dict format for storage
                    category_scores_dict = {
                        category: {
                            "score": score.score,
                            "reasoning": score.reasoning
                        }
                        for category, score in scoring_result.category_scores.items()
                    }
                    
                    # Create explanation
                    explanation_parts = [scoring_result.explanation]
                    if scoring_result.strengths:
                        explanation_parts.append(f"\n\nStrengths: {', '.join(scoring_result.strengths)}")
                    if scoring_result.weaknesses:
                        explanation_parts.append(f"\n\nWeaknesses: {', '.join(scoring_result.weaknesses)}")
                    full_explanation = "\n".join(explanation_parts)
                    
                    # Save score to database
                    candidate_score = models.CandidateScore(
                        candidate_id=candidate.id,
                        job_id=request.job_id,
                        total_score=scoring_result.total_score,
                        category_scores=category_scores_dict,
                        explanation=full_explanation
                    )
                    
                    db.add(candidate_score)
                    db.flush()
                    
                    candidate_data["total_score"] = candidate_score.total_score
                    candidate_data["category_scores"] = {
                        cat: CategoryScoreSchema(**score_data)
                        for cat, score_data in candidate_score.category_scores.items()
                    }
                    candidate_data["score_id"] = candidate_score.id
                    candidates_scored += 1
                    
                except Exception as e:
                    errors.append(f"Scoring failed for candidate {candidate.id}: {str(e)}")
                    candidate_data["total_score"] = None
                    candidate_data["category_scores"] = None
                    candidate_data["score_id"] = None
            
            candidates_with_scores.append(CandidateWithScore(**candidate_data))
        
        # Commit all changes
        db.commit()
        
        # Sort candidates by total_score (descending, None values last)
        candidates_with_scores.sort(
            key=lambda x: x.total_score if x.total_score is not None else -1,
            reverse=True
        )
        
        # Build response message
        message_parts = [
            f"Processed {len(candidates)} candidates",
            f"Scored {candidates_scored} new candidates",
            f"Checked authenticity for {candidates_checked} candidates"
        ]
        if errors:
            message_parts.append(f"({len(errors)} errors occurred)")
        
        return BulkScoringResponse(
            message=" | ".join(message_parts),
            job_id=request.job_id,
            candidates_scored=candidates_scored,
            candidates_checked=candidates_checked,
            candidates=candidates_with_scores
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during bulk scoring: {str(e)}"
        )

