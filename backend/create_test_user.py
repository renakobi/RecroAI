"""
Script to create a test user and company for development.
Run this once to set up initial credentials.
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models
from app.auth import get_password_hash

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_test_user():
    db: Session = SessionLocal()
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
            print(f"✅ Created company: {company.name} (ID: {company.id})")
        else:
            print(f"✅ Company already exists: {company.name} (ID: {company.id})")
        
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
                is_superuser=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created user: {user.username}")
            print("\n" + "="*50)
            print("LOGIN CREDENTIALS:")
            print("="*50)
            print(f"Username: admin")
            print(f"Password: admin123")
            print("="*50)
        else:
            print(f"✅ User already exists: {user.username}")
            print("\n" + "="*50)
            print("LOGIN CREDENTIALS:")
            print("="*50)
            print(f"Username: admin")
            print(f"Password: admin123")
            print("="*50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating test user and company...")
    create_test_user()
    print("\n✅ Setup complete! You can now login with the credentials above.")

