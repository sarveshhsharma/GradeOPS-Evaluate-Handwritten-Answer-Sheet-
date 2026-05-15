import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class UserRole(str, enum.Enum):
    PROFESSOR = "PROFESSOR"
    TA = "TA"

class SubmissionStatus(str, enum.Enum):
    PENDING = "PENDING"       # Uploaded, waiting for AI
    GRADED = "GRADED"         # AI has finished, waiting for TA review
    REVIEWED = "REVIEWED"     # TA has approved/overridden the grades

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PROFESSOR)
    
    # Relationships
    exams = relationship("Exam", back_populates="creator")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User", back_populates="exams")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="exam", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    q_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    max_marks = Column(Float, nullable=False)
    correct_answer = Column(Text, nullable=False) # This acts as our strict rubric

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    grades = relationship("Grade", back_populates="question", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(String, nullable=False) # e.g., Roll Number
    file_path = Column(String, nullable=False)  # Path in the uploads/ folder
    total_score = Column(Float, default=0.0)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    exam = relationship("Exam", back_populates="submissions")
    grades = relationship("Grade", back_populates="submission", cascade="all, delete-orphan")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    similarity_flag = Column(Boolean, default=False) # Plagiarism check > 0.85
    rubric_similarity = Column(Float, nullable=True) # NEW: % match to the correct answer
    
    # AI Extraction & Evaluation
    extracted_text = Column(Text, nullable=True)     # What Qwen2.5-VL read
    ai_score = Column(Float, nullable=True)          # What Langchain awarded
    ai_justification = Column(Text, nullable=True)   # Why it awarded those marks
    deduction_reasons = Column(Text, nullable=True)  # What was missing based on rubric
    similarity_flag = Column(Boolean, default=False) # Plagiarism check > 0.85
    
    # Human-in-the-loop
    final_score = Column(Float, nullable=True)       # What the TA ultimately approved

    # Relationships
    submission = relationship("Submission", back_populates="grades")
    question = relationship("Question", back_populates="grades")