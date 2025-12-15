from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas
from ..auth import (
    authenticate_user,
    get_password_hash,
    create_access_token,
    get_user_by_email,
    get_user_by_username,
    get_current_active_user,
)
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Extract company name from email domain or use default
    email_domain = user_data.email.split('@')[1] if '@' in user_data.email else 'default.com'
    company_name = email_domain.split('.')[0].title() + " Company"
    
    # Find or create company
    company = db.query(models.Company).filter(models.Company.name == company_name).first()
    if not company:
        company = models.Company(
            name=company_name,
            domain=email_domain,
            is_active=True
        )
        db.add(company)
        db.flush()  # Flush to get company.id without committing (keeps in same transaction)
        db.refresh(company)  # Explicitly refresh to ensure ID is loaded
    
    # Verify company has an ID
    if not company or not company.id:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create or retrieve company. Company exists: {company is not None}, ID: {getattr(company, 'id', None) if company else None}"
        )
    
    # Create new user with the company_id
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        company_id=company.id  # This should definitely have a value now
    )
    db.add(db_user)
    db.commit()  # Commit both company and user together
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user
