from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    sender_email: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SenderEmailUpdate(BaseModel):
    sender_email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    company_id: int
    name: Optional[str]
    email: Optional[str]
    source: str
    external_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CSVUploadResponse(BaseModel):
    message: str
    candidates_created: int
    candidates: List[CandidateResponse]


class LinkedInProfileInput(BaseModel):
    """LinkedIn profile data from API response"""
    # Accept flexible structure - any dict-like data
    class Config:
        extra = "allow"  # Allow extra fields from LinkedIn API


class LinkedInProfileCreate(BaseModel):
    """Request model for creating candidate from LinkedIn profile"""
    linkedin_data: Dict[str, Any]  # Flexible LinkedIn profile data
    linkedin_id: Optional[str] = None  # Optional LinkedIn ID if not in data


class CandidateCreateResponse(BaseModel):
    message: str
    candidate: CandidateResponse


class CategoryScoreSchema(BaseModel):
    """Category score schema"""
    score: float
    reasoning: str


class ScoringRequest(BaseModel):
    """Request to score a candidate"""
    candidate_id: int
    job_id: int


class ScoringResponseSchema(BaseModel):
    """Structured scoring response"""
    total_score: float
    category_scores: Dict[str, CategoryScoreSchema]
    explanation: str


class ScoringResultResponse(BaseModel):
    """Response after scoring is saved"""
    message: str
    score_id: int
    total_score: float
    category_scores: Dict[str, CategoryScoreSchema]
    explanation: str


class AuthenticityCheckRequest(BaseModel):
    """Request to check candidate authenticity"""
    candidate_id: int


class AuthenticityCheckResponse(BaseModel):
    """Response from authenticity check"""
    candidate_id: int
    is_suspicious: bool
    risk_score: float
    reason: str
    flag_id: Optional[int] = None  # ID of created/updated flag


class CandidateWithScore(BaseModel):
    """Candidate with score information"""
    candidate_id: int
    name: Optional[str]
    email: Optional[str]
    total_score: Optional[float] = None
    category_scores: Optional[Dict[str, CategoryScoreSchema]] = None
    is_suspicious: Optional[bool] = None
    risk_score: Optional[float] = None
    score_id: Optional[int] = None
    flag_id: Optional[int] = None
    raw_profile: Optional[str] = None  # For filtering
    explanation: Optional[str] = None  # Scoring explanation


class BulkScoringRequest(BaseModel):
    """Request to score all candidates for a job"""
    job_id: int


class BulkScoringResponse(BaseModel):
    """Response from bulk scoring"""
    message: str
    job_id: int
    candidates_scored: int
    candidates_checked: int
    candidates: List[CandidateWithScore]  # Sorted by total_score descending

