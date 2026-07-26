"""
Script to seed the database with test jobs and candidates.
Run this after create_test_user.py to populate sample data.
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models
import json

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def seed_test_data():
    db: Session = SessionLocal()
    try:
        # Get the test company
        company = db.query(models.Company).filter(models.Company.name == "Test Company").first()
        
        if not company:
            print("[ERROR] Test Company not found. Please run create_test_user.py first.")
            sys.exit(1)
        
        # Create test jobs (only if they don't exist by title)
        jobs_data = [
                {
                    "title": "Senior Software Engineer",
                    "criteria_json": {
                        "education": "Bachelor's degree in Computer Science or related field",
                        "experience": "5+ years of software development experience",
                        "skills": "Python, React, SQL, AWS, Docker, Kubernetes",
                        "other": "Experience with microservices architecture, CI/CD pipelines"
                    }
                },
                {
                    "title": "Data Scientist",
                    "criteria_json": {
                        "education": "Master's degree in Data Science, Statistics, or related field",
                        "experience": "3+ years of data science experience",
                        "skills": "Python, Machine Learning, SQL, TensorFlow, PyTorch, Pandas",
                        "other": "Experience with statistical analysis and model deployment"
                    }
                },
                {
                    "title": "Frontend Developer",
                    "criteria_json": {
                        "education": "Bachelor's degree in Computer Science or related field",
                        "experience": "2+ years of frontend development experience",
                        "skills": "React, JavaScript, TypeScript, CSS, HTML, Redux",
                        "other": "Experience with responsive design and modern UI frameworks"
                    }
                },
                {
                    "title": "DevOps Engineer",
                    "criteria_json": {
                        "education": "Bachelor's degree in Computer Science or related field",
                        "experience": "4+ years of DevOps or infrastructure experience",
                        "skills": "AWS, Docker, Kubernetes, Terraform, Jenkins, Linux",
                        "other": "Experience with cloud infrastructure and automation"
                    }
                }
        ]
        
        created_jobs = []
        for job_data in jobs_data:
            # Check if job with this title already exists
            existing_job = db.query(models.Job).filter(
                models.Job.company_id == company.id,
                models.Job.title == job_data["title"]
            ).first()
            
            if not existing_job:
                job = models.Job(
                    title=job_data["title"],
                    company_id=company.id,
                    criteria_json=job_data["criteria_json"],
                    status="active"
                )
                db.add(job)
                created_jobs.append(job)
        
        if created_jobs:
            db.commit()
            for job in created_jobs:
                db.refresh(job)
            print(f"[OK] Created {len(created_jobs)} test job(s)")
        else:
            print(f"[OK] All jobs already exist. Skipping job creation.")
        
        # Check if candidates already exist
        existing_candidates = db.query(models.Candidate).filter(models.Candidate.company_id == company.id).count()
        if existing_candidates > 0:
            print(f"[OK] {existing_candidates} candidate(s) already exist. Skipping candidate creation.")
        else:
            # Create test candidates
            candidates_data = [
                {
                    "name": "Alice Johnson",
                    "email": "alice.johnson@email.com",
                    "raw_profile": json.dumps({
                        "name": "Alice Johnson",
                        "education": "Master's in Computer Science from Stanford University",
                        "experience": "6 years as Senior Software Engineer at Google, worked on distributed systems and microservices",
                        "skills": "Python, React, SQL, AWS, Docker, Kubernetes, Go, Microservices",
                        "summary": "Experienced software engineer with expertise in building scalable systems. Led multiple projects at Google."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Bob Smith",
                    "email": "bob.smith@email.com",
                    "raw_profile": json.dumps({
                        "name": "Bob Smith",
                        "education": "Bachelor's in Computer Science from MIT",
                        "experience": "4 years as Software Engineer at Microsoft, focused on cloud infrastructure",
                        "skills": "Python, AWS, Docker, Kubernetes, Terraform, Linux, CI/CD",
                        "summary": "DevOps engineer passionate about automation and cloud infrastructure. Strong background in AWS and containerization."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Carol Williams",
                    "email": "carol.williams@email.com",
                    "raw_profile": json.dumps({
                        "name": "Carol Williams",
                        "education": "PhD in Data Science from Carnegie Mellon University",
                        "experience": "5 years as Data Scientist at Amazon, built ML models for recommendation systems",
                        "skills": "Python, Machine Learning, TensorFlow, PyTorch, SQL, Pandas, Statistics",
                        "summary": "Data scientist with deep expertise in machine learning and statistical analysis. Published researcher."
                    }),
                    "source": "csv"
                },
                {
                    "name": "David Brown",
                    "email": "david.brown@email.com",
                    "raw_profile": json.dumps({
                        "name": "David Brown",
                        "education": "Bachelor's in Computer Science from UC Berkeley",
                        "experience": "3 years as Frontend Developer at Facebook, built React applications",
                        "skills": "React, JavaScript, TypeScript, CSS, HTML, Redux, Next.js",
                        "summary": "Frontend developer specializing in React and modern web technologies. Passionate about user experience."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Emma Davis",
                    "email": "emma.davis@email.com",
                    "raw_profile": json.dumps({
                        "name": "Emma Davis",
                        "education": "Master's in Software Engineering from University of Washington",
                        "experience": "7 years as Software Engineer at Apple, worked on iOS and backend systems",
                        "skills": "Python, Swift, React, SQL, AWS, Docker, Microservices, REST APIs",
                        "summary": "Full-stack engineer with extensive experience in both mobile and backend development."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Frank Miller",
                    "email": "frank.miller@email.com",
                    "raw_profile": json.dumps({
                        "name": "Frank Miller",
                        "education": "Bachelor's in Computer Science from Georgia Tech",
                        "experience": "2 years as Junior Software Engineer at startup, worked on web applications",
                        "skills": "Python, JavaScript, React, SQL, Git",
                        "summary": "Junior developer eager to learn and grow. Strong foundation in web development."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Grace Lee",
                    "email": "grace.lee@email.com",
                    "raw_profile": json.dumps({
                        "name": "Grace Lee",
                        "education": "Master's in Data Science from Columbia University",
                        "experience": "4 years as Data Scientist at Netflix, built recommendation algorithms",
                        "skills": "Python, Machine Learning, SQL, TensorFlow, PyTorch, Spark, Statistics",
                        "summary": "Data scientist focused on recommendation systems and personalization. Strong statistical background."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Henry Wilson",
                    "email": "henry.wilson@email.com",
                    "raw_profile": json.dumps({
                        "name": "Henry Wilson",
                        "education": "Bachelor's in Computer Science from University of Texas",
                        "experience": "5 years as DevOps Engineer at Netflix, managed cloud infrastructure",
                        "skills": "AWS, Docker, Kubernetes, Terraform, Jenkins, Linux, Python, Bash",
                        "summary": "DevOps engineer with expertise in cloud infrastructure and automation. Experienced with large-scale systems."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Ivy Chen",
                    "email": "ivy.chen@email.com",
                    "raw_profile": json.dumps({
                        "name": "Ivy Chen",
                        "education": "Bachelor's in Computer Science from University of California",
                        "experience": "3 years as Frontend Developer at Airbnb, built React components and design systems",
                        "skills": "React, JavaScript, TypeScript, CSS, HTML, Redux, Storybook, Design Systems",
                        "summary": "Frontend developer with strong design sense. Experienced in building component libraries."
                    }),
                    "source": "csv"
                },
                {
                    "name": "Jack Taylor",
                    "email": "jack.taylor@email.com",
                    "raw_profile": json.dumps({
                        "name": "Jack Taylor",
                        "education": "Master's in Computer Science from Harvard University",
                        "experience": "8 years as Senior Software Engineer at Microsoft, led multiple teams",
                        "skills": "Python, C#, React, SQL, AWS, Azure, Docker, Kubernetes, Leadership",
                        "summary": "Senior engineer with leadership experience. Built and scaled multiple products at Microsoft."
                    }),
                    "source": "csv"
                }
            ]
            
            created_candidates = []
            for candidate_data in candidates_data:
                candidate = models.Candidate(
                    company_id=company.id,
                    name=candidate_data["name"],
                    email=candidate_data["email"],
                    raw_profile=candidate_data["raw_profile"],
                    parsed_profile_json=None,
                    source=candidate_data["source"],
                    external_id=None
                )
                db.add(candidate)
                created_candidates.append(candidate)
            
            db.commit()
            for candidate in created_candidates:
                db.refresh(candidate)
            
            print(f"[OK] Created {len(created_candidates)} test candidate(s)")
        
        print("\n" + "="*50)
        print("[OK] Test data seeding complete!")
        print("="*50)
        print(f"Jobs: {db.query(models.Job).filter(models.Job.company_id == company.id).count()}")
        print(f"Candidates: {db.query(models.Candidate).filter(models.Candidate.company_id == company.id).count()}")
        print("="*50)
        print("\nYou can now:")
        print("1. Login to the application")
        print("2. Select a job to view and score candidates")
        print("3. Test the filtering and email functionality")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding test data...")
    seed_test_data()

