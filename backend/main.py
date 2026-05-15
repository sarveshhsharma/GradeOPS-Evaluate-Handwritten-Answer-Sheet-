from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Use absolute local imports (no dots)
from database import engine, Base, SessionLocal
from models import User, UserRole
from routes import exams, submissions, grading

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

# ====================================================================
# SEED THE DATABASE WITH A DUMMY USER (Fixes the Foreign Key Crash)
# ====================================================================
db = SessionLocal()
try:
    # If the users table is completely empty, create User ID 1
    if not db.query(User).first():
        test_user = User(name="Professor Sarvesh", role=UserRole.PROFESSOR)
        db.add(test_user)
        db.commit()
        print("Successfully created dummy user (ID 1)")
except Exception as e:
    print(f"Failed to seed user: {e}")
finally:
    db.close()
# ====================================================================

app = FastAPI(title="GRADEOPS API")

origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, PUT, etc.
    allow_headers=["*"], # Allows Content-Type, etc.
)

# Include API Routers explicitly
app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(grading.router, prefix="/api/grading", tags=["Grading"])