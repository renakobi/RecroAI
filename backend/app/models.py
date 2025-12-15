from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint, Index
from .database import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    domain = Column(String, index=True, nullable = True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")
    candidates = relationship("Candidate", back_populates="company")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    sender_email = Column(String, index=True)  # Email address used for sending
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    email_logs = relationship("EmailLog", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    criteria_json = Column(JSON, nullable=False)  # Stores job criteria as JSON
    status = Column(String, default="active")  # active, closed, draft
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    candidate_scores = relationship("CandidateScore", back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    raw_profile = Column(Text, nullable=False)  # Raw candidate profile data
    parsed_profile_json = Column(JSON)  # Parsed/structured profile data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source = Column(String, nullable=False, index=True)  # "linkedin" | "csv"
    external_id = Column(String, index=True)  # linkedin id or csv row id (optional)

    # Relationships
    company = relationship("Company", back_populates="candidates")
    scores = relationship("CandidateScore", back_populates="candidate")
    authenticity_flag = relationship("AuthenticityFlag", back_populates="candidate", uselist=False)


class CandidateScore(Base):
    __tablename__ = "candidate_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    total_score = Column(Float, nullable = False)
    category_scores = Column(JSON, nullable=False)  # Stores category scores as JSON
    explanation = Column(Text)  # Explanation of the scoring
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job_score"),
        Index("ix_scores_job_total", "job_id", "total_score"),
)
    candidate = relationship("Candidate", back_populates="scores")
    job = relationship("Job", back_populates="candidate_scores")

class AuthenticityFlag(Base):
    __tablename__ = "authenticity_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), unique=True, nullable=False, index=True)
    is_suspicious = Column(Boolean, default=False, nullable=False)
    risk_score = Column(Float)  # Risk score (0.0 to 1.0 or similar scale)
    reason = Column(Text)  # Reason for flagging
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="authenticity_flag")


class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_email = Column(String, nullable=False, index=True)
    subject = Column(String)
    body = Column(Text)
    status = Column(String, default="sent")  # sent, failed, pending
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="email_logs")
    candidate = relationship("Candidate")
    job = relationship("Job")

    candidate_id = Column(Integer, ForeignKey("candidates.id"), index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), index=True)
    email_type = Column(String, nullable=False)  # interview | rejection
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", "email_type", name="uq_candidate_job_email"),
        Index("ix_logs_email_type", "email_type"),
)
