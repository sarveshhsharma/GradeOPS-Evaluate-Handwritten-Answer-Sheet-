from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Grade, Submission, SubmissionStatus
from schemas import GradeResponse, GradeUpdate

router = APIRouter()

@router.get("/{submission_id}/grades", response_model=List[GradeResponse])
def get_submission_grades(submission_id: int, db: Session = Depends(get_db)):
    """Returns all per-question grades, AI justifications, and similarity flags for a submission."""
    grades = db.query(Grade).filter(Grade.submission_id == submission_id).all()
    if not grades:
        raise HTTPException(status_code=404, detail="No grades found for this submission.")
    return grades

@router.put("/override/{grade_id}", response_model=GradeResponse)
def override_grade(grade_id: int, grade_update: GradeUpdate, db: Session = Depends(get_db)):
    """Human-in-the-Loop endpoint: Allows a TA to override the AI's score."""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Update the final score based on TA input
    grade.final_score = grade_update.final_score
    db.commit()
    db.refresh(grade)

    # Recalculate the submission's total score based on the new override
    submission = db.query(Submission).filter(Submission.id == grade.submission_id).first()
    all_grades = db.query(Grade).filter(Grade.submission_id == submission.id).all()
    
    new_total = sum(g.final_score for g in all_grades if g.final_score is not None)
    submission.total_score = new_total
    submission.status = SubmissionStatus.REVIEWED # Mark as reviewed by human
    
    db.commit()

    return grade