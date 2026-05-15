from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import Submission, SubmissionStatus, Question, Grade
from schemas import SubmissionResponse
from utils.file_helpers import save_uploaded_file, convert_pdf_to_images
from services.ocr_service import extract_text_from_image
from services.segmentation_service import segment_answers
from services.grading_service import evaluate_answer
from services.similarity_service import check_similarity, calculate_rubric_similarity

router = APIRouter()

def process_grading_pipeline(submission_id: int, pdf_path: str, exam_id: int):
    """Background task that runs the AI extraction, grading, and similarity checks."""
    db = SessionLocal()
    try:
        print(f"\n🚀 [START] Initiating Grading Pipeline for Submission ID: {submission_id}")
        
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        questions = db.query(Question).filter(Question.exam_id == exam_id).all()
        
        # 1. Convert PDF to images
        print("📄 [STEP 1/5] Processing uploaded file format...")
        file_extension = pdf_path.split(".")[-1].lower()
        
        image_paths = []
        if file_extension == "pdf":
            print("   -> PDF detected. Converting to images...")
            image_paths = convert_pdf_to_images(pdf_path)
            print(f"   -> Generated {len(image_paths)} image(s).")
        elif file_extension in ["jpg", "jpeg", "png"]:
            print("   -> Image detected. Bypassing PDF conversion...")
            image_paths = [pdf_path] # The uploaded file IS the image
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Only PDF, JPG, and PNG are allowed.")
        
        # 2. OCR Extraction (combine text from all pages)
        print("👁️ [STEP 2/5] Running Vision AI to extract handwriting (This takes the longest)...")
        raw_text_parts = []
        for i, img_path in enumerate(image_paths):
            print(f"   -> Scanning page {i + 1} of {len(image_paths)}...")
            text = extract_text_from_image(img_path)
            raw_text_parts.append(text)
        full_raw_text = "\n".join(raw_text_parts)
        print("   -> Vision extraction complete.")
        
        # 3. Segmentation (Split into dictionary by question number)
        print("🧠 [STEP 3/5] Segmenting raw text into individual answers...")
        segmented_answers = segment_answers(full_raw_text)
        print(f"   -> Successfully isolated answers for {len(segmented_answers)} questions.")
        
        total_ai_score = 0.0
        
        # 4. Grading & Similarity Check per question
        print(f"⚖️ [STEP 4/5] Evaluating {len(questions)} questions against strict rubric...")
        for question in questions:
            print(f"   -> Grading Question {question.q_number} (Max Marks: {question.max_marks})...")
            student_answer = segmented_answers.get(question.q_number, "")
            
            # If no answer found, give 0
            if not student_answer.strip():
                print("      -> No answer found. Awarding 0 marks.")
                grade = Grade(
                    submission_id=submission_id,
                    question_id=question.id,
                    extracted_text="[No answer found]",
                    ai_score=0.0,
                    ai_justification="The AI could not locate an answer for this question number.",
                    deduction_reasons="Missing completely.",
                    similarity_flag=False,
                    rubric_similarity=0.0, # Handle missing answers gracefully
                    final_score=0.0
                )
                db.add(grade)
                continue

            # Check similarity against previously graded answers (Plagiarism)
            print("      -> Running Plagiarism/Similarity check...")
            previous_grades = db.query(Grade).filter(Grade.question_id == question.id).all()
            existing_texts = [g.extracted_text for g in previous_grades if g.extracted_text]
            is_similar = check_similarity(student_answer, existing_texts)

            # Calculate Rubric Similarity %
            rubric_match_percent = calculate_rubric_similarity(student_answer, question.correct_answer)
            print(f"      -> Rubric Match: {rubric_match_percent}%")

            # AI Grading
            print("      -> AI calculating score based on rubric...")
            eval_result = evaluate_answer(student_answer, question.correct_answer, question.max_marks)
            
            ai_score = eval_result.get("score_awarded", 0.0)
            print(f"      -> AI Base Score: {ai_score}/{question.max_marks} | Plagiarism Flag: {is_similar}")
            
            # =========================================================
            # NEW: WEIGHTED SCORING LOGIC (60% Rubric, 40% AI)
            # =========================================================
            # 1. Convert Rubric % into a raw score out of max_marks
            rubric_score = (rubric_match_percent / 100.0) * question.max_marks
            
            # 2. Apply weights
            weighted_score = (0.60 * rubric_score) + (0.40 * ai_score)
            
            # 3. Round to 1 decimal place (e.g., 3.84 -> 3.8)
            calculated_final_score = round(weighted_score, 1)
            print(f"      -> Weighted Final Score: {calculated_final_score}/{question.max_marks}")
            # =========================================================
            
            total_ai_score += calculated_final_score
            
            grade = Grade(
                submission_id=submission_id,
                question_id=question.id,
                extracted_text=student_answer,
                ai_score=ai_score, # Keep a record of the pure AI score
                ai_justification=eval_result.get("justification", ""),
                deduction_reasons=eval_result.get("deductions", ""),
                similarity_flag=is_similar,
                rubric_similarity=rubric_match_percent, 
                final_score=calculated_final_score # Save the new weighted score as the final
            )
            db.add(grade)

        # 5. Finalize Submission
        print("💾 [STEP 5/5] Saving final grades to database...")
        submission.total_score = total_ai_score
        submission.status = SubmissionStatus.GRADED
        db.commit()
        
        print(f"✅ [DONE] Pipeline complete! Total AI Score: {total_ai_score}\n")

    except Exception as e:
        print(f"\n❌ [ERROR] Pipeline completely failed for submission {submission_id}: {e}\n")
    finally:
        db.close()

@router.post("/{exam_id}/upload")
def upload_submission(
    exam_id: int, 
    background_tasks: BackgroundTasks,
    student_id: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """Uploads a PDF and triggers the AI grading pipeline in the background."""
    # Save the file
    file_path = save_uploaded_file(file)
    
    # Create the pending submission
    submission = Submission(
        exam_id=exam_id,
        student_id=student_id,
        file_path=file_path,
        status=SubmissionStatus.PENDING
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Trigger the heavy AI pipeline in the background
    background_tasks.add_task(process_grading_pipeline, submission.id, file_path, exam_id)
    
    return {"message": "File uploaded and grading started", "submission_id": submission.id}

@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """Fetches the submission details and current status."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission