from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models import Exam, Question
from schemas import ExamCreate, ExamResponse

# Import LangChain PromptTemplate and your Shared LLM
from langchain_core.prompts import PromptTemplate
from services.shared_llm import shared_llm 

router = APIRouter()

# Schema for the AI Generation Request
class RubricGenerateRequest(BaseModel):
    question_text: str

@router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(exam_in: ExamCreate, db: Session = Depends(get_db)):
    """Creates a new exam and its associated rubric questions."""
    # Create the exam record
    db_exam = Exam(
        title=exam_in.title,
        total_questions=exam_in.total_questions,
        created_by=exam_in.created_by
    )
    db.add(db_exam)
    db.flush() # Flush to get the db_exam.id without committing yet

    # Create the questions/rubrics
    for q in exam_in.questions:
        db_question = Question(
            exam_id=db_exam.id,
            q_number=q.q_number,
            question_text=q.question_text,
            max_marks=q.max_marks,
            correct_answer=q.correct_answer
        )
        db.add(db_question)

    db.commit()
    db.refresh(db_exam)
    return db_exam

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    """Fetches exam details and its rubric."""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

@router.post("/generate-rubric")
def generate_rubric(request: RubricGenerateRequest):
    """Uses the local LLM to generate a strict rubric based on the question."""
    
    # Using the exact ChatML format that Qwen 1.5B expects
    prompt = PromptTemplate.from_template(
        """<|im_start|>system
        You are an expert university professor. The user will provide a test question. 
        Write a highly concise, strict grading rubric or the exact correct answer required for full marks. 
        Output ONLY the rubric text. Do not include conversational filler.
        <|im_end|>
        <|im_start|>user
        Question: {question_text}
        <|im_end|>
        <|im_start|>assistant
        """
    )
    
    chain = prompt | shared_llm
    
    try:
        # Generate the response
        response = chain.invoke({"question_text": request.question_text})
        
        # Clean up any accidental markdown or whitespace
        clean_rubric = response.replace("```text", "").replace("```", "").strip()
        
        return {"generated_rubric": clean_rubric}
    except Exception as e:
        print(f"Rubric generation failed: {e}")
        return {"generated_rubric": "Error: The local AI model failed to generate a rubric. Please check the backend console."}