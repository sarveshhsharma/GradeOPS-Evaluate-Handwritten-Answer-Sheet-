from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from models import UserRole, SubmissionStatus

# --- USERS ---
class UserBase(BaseModel):
    name: str
    role: UserRole

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- QUESTIONS (RUBRIC) ---
class QuestionCreate(BaseModel):
    q_number: int
    question_text: str
    max_marks: float
    correct_answer: str

class QuestionResponse(QuestionCreate):
    id: int
    exam_id: int
    model_config = ConfigDict(from_attributes=True)


# --- EXAMS ---
class ExamCreate(BaseModel):
    title: str
    total_questions: int
    created_by: int
    questions: List[QuestionCreate]

class ExamResponse(BaseModel):
    id: int
    title: str
    total_questions: int
    created_by: int
    created_at: datetime
    questions: List[QuestionResponse]
    model_config = ConfigDict(from_attributes=True)


# --- GRADES ---
class GradeUpdate(BaseModel):
    """Schema for the TA Human-In-The-Loop override"""
    final_score: float

class GradeResponse(BaseModel):
    id: int
    submission_id: int
    question_id: int
    extracted_text: Optional[str]
    ai_score: Optional[float]
    ai_justification: Optional[str]
    deduction_reasons: Optional[str]
    similarity_flag: bool
    final_score: Optional[float]
    rubric_similarity: Optional[float] = None
    
    # Include question details so the frontend has context (max_marks, etc.)
    question: Optional[QuestionResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- SUBMISSIONS ---
class SubmissionCreate(BaseModel):
    exam_id: int
    student_id: str
    # file_path is handled internally during the upload route, not via JSON request

class SubmissionResponse(BaseModel):
    id: int
    exam_id: int
    student_id: str
    file_path: str
    total_score: float
    status: SubmissionStatus
    created_at: datetime
    grades: List[GradeResponse] = []
    
    model_config = ConfigDict(from_attributes=True)