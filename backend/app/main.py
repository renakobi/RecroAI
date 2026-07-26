import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from .config import settings
from .database import engine, Base, SessionLocal
from .routers import auth, users, candidates, scoring, emails, jobs, analytics
from . import models
from .auth import get_password_hash, get_current_user

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-create test user on startup
def create_test_user_on_startup():
    """Create test user and company if they don't exist"""
    db = SessionLocal()
    try:
        # Check if company already exists
        company = db.query(models.Company).filter(models.Company.name == "Test Company").first()
        
        if not company:
            # Create test company
            company = models.Company(
                name="Test Company",
                domain="test.com",
                is_active=True
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            sys.stdout.buffer.write(f"[OK] Created company: {company.name} (ID: {company.id})\n".encode('utf-8'))
        
        # Check if user already exists
        user = db.query(models.User).filter(models.User.username == "admin").first()
        
        if not user:
            # Create test user
            user = models.User(
                email="admin@test.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                company_id=company.id,
                is_active=True,
                is_superuser=True,
                sender_email="admin@test.com"  # Set sender email for email functionality
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            sys.stdout.buffer.write(f"[OK] Created test user: {user.username}\n".encode('utf-8'))
            sys.stdout.buffer.write("[INFO] Test user created. Check create_test_user.py for credentials.\n".encode('utf-8'))
    except Exception as e:
        sys.stdout.buffer.write(f"[WARNING] Could not create test user: {e}\n".encode('utf-8'))
        db.rollback()
    finally:
        db.close()

# Create test user on startup
create_test_user_on_startup()

# Add HTTPBearer for simple token entry in Swagger
http_bearer = HTTPBearer(auto_error=False)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    swagger_ui_init_oauth={
        "clientId": "swagger-ui",
        "usePkceWithAuthorizationCodeGrant": False,
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(scoring.router)
app.include_router(emails.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Helper endpoint to get token info for Swagger
@app.get("/auth/token-info")
def get_token_info():
    """
    Helper endpoint for Swagger UI.
    
    To use:
    1. Call POST /auth/login with username=admin, password=admin123
    2. Copy the 'access_token' from the response
    3. Click 'Authorize' button in Swagger
    4. In the OAuth2 dialog, enter:
       - username: admin
       - password: admin123
       - client_secret: (leave empty)
    5. Click 'Authorize'
    
    Or manually add header: Authorization: Bearer <your_token>
    """
    return {
        "message": "Use /auth/login to get a token",
        "note": "After login, use the 'Authorize' button or add 'Authorization: Bearer <token>' header"
    }

