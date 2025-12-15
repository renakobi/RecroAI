import csv
import io
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from .. import models
from ..auth import get_current_active_user
from ..database import get_db
from ..schemas import CandidateResponse, CSVUploadResponse, LinkedInProfileCreate, CandidateCreateResponse, AuthenticityCheckRequest, AuthenticityCheckResponse
from ..services.linkedin_service import create_candidate_from_linkedin
from ..services.authenticity_service import get_authenticity_service

router = APIRouter(prefix="/candidates", tags=["candidates"])

# Expected CSV columns
CSV_COLUMNS = ["name", "education", "experience", "skills", "summary"]


@router.post("/upload-csv", response_model=CSVUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_candidates_csv(
    file: UploadFile = File(..., description="CSV file with columns: name, education, experience, skills, summary"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Upload a CSV file to create candidates.
    
    Expected CSV schema:
    - name: Candidate name
    - education: Education details
    - experience: Work experience
    - skills: Skills list
    - summary: Profile summary
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Read file content
    contents = await file.read()
    
    try:
        # Decode and parse CSV
        csv_content = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Validate CSV headers
        if not csv_reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty or invalid"
            )
        
        # Check if all required columns are present (case-insensitive)
        csv_headers = [col.strip().lower() for col in csv_reader.fieldnames]
        required_headers = [col.lower() for col in CSV_COLUMNS]
        
        missing_headers = [col for col in required_headers if col not in csv_headers]
        if missing_headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_headers)}"
            )
        
        # Create a mapping from standard column names to CSV headers (case-insensitive)
        header_mapping = {}
        for csv_header in csv_reader.fieldnames:
            normalized = csv_header.strip().lower()
            if normalized in required_headers:
                standard_name = CSV_COLUMNS[required_headers.index(normalized)]
                header_mapping[standard_name] = csv_header
        
        # Process rows and create candidates
        created_candidates = []
        row_index = 0
        
        for row in csv_reader:
            row_index += 1
            
            # Extract values using header mapping (standard name -> CSV header)
            name = row.get(header_mapping.get("name", ""), "").strip()
            education = row.get(header_mapping.get("education", ""), "").strip()
            experience = row.get(header_mapping.get("experience", ""), "").strip()
            skills = row.get(header_mapping.get("skills", ""), "").strip()
            summary = row.get(header_mapping.get("summary", ""), "").strip()
            
            # Skip empty rows
            if not any([name, education, experience, skills, summary]):
                continue
            
            # Store the full row as raw_profile (as JSON string for better structure)
            raw_profile_data = {
                "name": name,
                "education": education,
                "experience": experience,
                "skills": skills,
                "summary": summary
            }
            raw_profile_text = json.dumps(raw_profile_data, ensure_ascii=False)
            
            # Create candidate
            candidate = models.Candidate(
                company_id=current_user.company_id,
                name=name if name else None,
                email=None,  # CSV doesn't include email
                raw_profile=raw_profile_text,
                parsed_profile_json=None,  # Can be populated later
                source="csv",
                external_id=str(row_index)  # Use row index as external_id
            )
            
            db.add(candidate)
            created_candidates.append(candidate)
        
        # Commit all candidates
        db.commit()
        
        # Refresh all candidates to get their IDs
        for candidate in created_candidates:
            db.refresh(candidate)
        
        return CSVUploadResponse(
            message=f"Successfully created {len(created_candidates)} candidates",
            candidates_created=len(created_candidates),
            candidates=[CandidateResponse.model_validate(c) for c in created_candidates]
        )
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/", response_model=List[CandidateResponse])
def get_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all candidates for the authenticated user's company"""
    candidates = db.query(models.Candidate).filter(
        models.Candidate.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    return candidates


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific candidate by ID (only if belongs to user's company)"""
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id,
        models.Candidate.company_id == current_user.company_id
    ).first()
    
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate


@router.post("/from-linkedin", response_model=CandidateCreateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate_from_linkedin_profile(
    request: LinkedInProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a candidate from LinkedIn profile data.
    
    Accepts LinkedIn profile data from an API response, normalizes it into the same
    raw_profile format as CSV uploads, and saves it as a Candidate linked to the
    authenticated user's company.
    """
    try:
        # Create candidate data from LinkedIn profile
        candidate_data = create_candidate_from_linkedin(
            linkedin_data=request.linkedin_data,
            company_id=current_user.company_id,
            linkedin_id=request.linkedin_id
        )
        
        # Check if candidate with same external_id already exists
        if candidate_data["external_id"]:
            existing = db.query(models.Candidate).filter(
                models.Candidate.company_id == current_user.company_id,
                models.Candidate.external_id == candidate_data["external_id"],
                models.Candidate.source == "linkedin"
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Candidate with LinkedIn ID {candidate_data['external_id']} already exists"
                )
        
        # Create candidate
        candidate = models.Candidate(**candidate_data)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return CandidateCreateResponse(
            message="Candidate created successfully from LinkedIn profile",
            candidate=CandidateResponse.model_validate(candidate)
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing LinkedIn profile: {str(e)}"
        )


@router.post("/check-authenticity", response_model=AuthenticityCheckResponse)
async def check_candidate_authenticity(
    request: AuthenticityCheckRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Check candidate profile for prompt injection attempts and suspicious content.
    
    Uses both keyword heuristics and LLM classification.
    Only flags - does not block candidates.
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
    
    try:
        # Get authenticity service
        authenticity_service = get_authenticity_service()
        
        # Analyze the raw profile text
        text_to_analyze = candidate.raw_profile
        
        # Run analysis
        result = await authenticity_service.analyze_text(text_to_analyze, use_llm=True)
        
        # Check if flag already exists
        existing_flag = db.query(models.AuthenticityFlag).filter(
            models.AuthenticityFlag.candidate_id == request.candidate_id
        ).first()
        
        if existing_flag:
            # Update existing flag
            existing_flag.is_suspicious = result.is_suspicious
            existing_flag.risk_score = result.risk_score
            existing_flag.reason = result.reason
            db.commit()
            db.refresh(existing_flag)
            flag_id = existing_flag.id
        else:
            # Create new flag
            new_flag = models.AuthenticityFlag(
                candidate_id=request.candidate_id,
                is_suspicious=result.is_suspicious,
                risk_score=result.risk_score,
                reason=result.reason
            )
            db.add(new_flag)
            db.commit()
            db.refresh(new_flag)
            flag_id = new_flag.id
        
        return AuthenticityCheckResponse(
            candidate_id=request.candidate_id,
            is_suspicious=result.is_suspicious,
            risk_score=result.risk_score,
            reason=result.reason,
            flag_id=flag_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking authenticity: {str(e)}"
        )

