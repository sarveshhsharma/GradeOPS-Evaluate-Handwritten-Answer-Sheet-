# GRADEOPS: AI-Assisted Student Answer-Sheet Grading App 

An intelligent, full-stack platform designed to automate the evaluation of handwritten examination papers. GRADEOPS utilizes a localized AI processing pipeline to read student answer sheets, extract text, evaluate answers against a rubric, detect plagiarism, and enable a Human-in-the-Loop (HITL) review process. 

Designed as a lightweight monolithic application, it is perfect as a robust student project, a working demo, or a foundational architecture for scalable grading systems.

---

## Features

* **Automated Exam Processing:** Upload handwritten answer sheets (PDF/Images) for automatic evaluation.
* **Computer Vision / OCR:** Uses advanced Vision-Language Models to extract raw handwritten text accurately.
* **Smart Answer Segmentation:** Automatically maps extracted text blocks to specific question numbers.
* **AI-Powered Grading:** Evaluates student answers against a professor's rubric, awarding partial credit and providing deduction reasons.
* **Plagiarism Detection:** Uses vector embeddings and cosine similarity to flag suspiciously similar submissions.
* **Human-in-the-Loop (HITL):** A Teaching Assistant (TA) dashboard to review AI-assigned grades, read justification, and manually override scores if necessary.

---

## Technology Stack

**Frontend (User Interface)**
* **React.js + Vite:** Fast, single-page application.
* **Tailwind CSS:** Lightweight, responsive styling.
* **Axios:** API communication.

**Backend (Application Engine)**
* **FastAPI (Python):** High-performance backend utilizing `BackgroundTasks` for asynchronous AI processing.
* **PostgreSQL:** Relational database for storing rubrics, submissions, and grades.
* **SQLAlchemy:** ORM for database operations.

**AI Layer (Localized Models)**
* **Hugging Face Transformers:** Runs local AI models (optimized for Apple Silicon / `mps` backend).
* **LangChain:** Structures prompting and forces outputs into predictable JSON.
* **Qwen2.5-VL-3B-Instruct:** Vision-language model for OCR and handwriting transcription.
* **Qwen2.5-1.5B-Instruct:** Text reasoning model for segmentation, grading, and generating deduction reasons.
* **all-MiniLM-L6-v2:** Semantic similarity model to convert answers into embeddings and flag plagiarism.

---

## System Architecture & Workflow

### 1. Exam Setup
1. The Professor enters the exam title, questions, maximum marks, and ideal answers (rubric) via the React frontend.
2. FastAPI validates and stores this schema in PostgreSQL.

### 2. Upload & Ingestion
1. The Professor/TA uploads a scanned student PDF and student ID.
2. The file is saved securely in the backend (`uploads/pdfs/`).
3. FastAPI immediately acknowledges the upload and triggers an asynchronous AI background task.

### 3. AI Processing Pipeline
* **Step 1: Conversion:** The PDF is converted into images using `pdf2image` and `Pillow`.
* **Step 2: Vision Extraction:** `Qwen2.5-VL-3B-Instruct` reads the handwritten content and generates raw digital text.
* **Step 3: Answer Segmentation:** `Qwen2.5-1.5B-Instruct` reorganizes the raw text into a structured JSON mapping (e.g., `{"1": "Answer to Q1..."}`).
* **Step 4: Similarity & Plagiarism:** `all-MiniLM-L6-v2` compares answer embeddings. High cosine similarity (>0.85) triggers a plagiarism flag.
* **Step 5: AI Grading:** `Qwen2.5-1.5B-Instruct` (via LangChain) compares the student's answer to the rubric, calculates a score, and provides a deduction reason.
* **Step 6: Storage:** Results are saved to the `Grades` and `Submissions` tables in PostgreSQL.

### 4. Human-in-the-Loop (HITL)
TAs can open the grading dashboard to view the extracted text, the AI's proposed score, and the deduction justification. If the AI is inaccurate, the TA can manually override the score, marking the submission as `REVIEWED`.

---

## 📂 Project Structure

```text
gradeops/
├── frontend/
│   ├── src/
│   │   ├── components/       # QuestionForm, UploadBox, ScoreCard, AnswerBreakdown
│   │   ├── pages/            # CreateExam, UploadSheet, Results
│   │   ├── api/              # Axios client setup
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
└── backend/
    ├── main.py               # FastAPI entry point
    ├── database.py           # DB connection setup
    ├── models.py             # SQLAlchemy models
    ├── schemas.py            # Pydantic validation
    ├── routes/               
    │   ├── exams.py          # Exam creation/retrieval
    │   ├── submissions.py    # Uploads and results
    │   └── grading.py        # Grading logic & overrides
    ├── services/
    │   ├── ocr_service.py           # VLM OCR logic
    │   ├── segmentation_service.py  # Answer splitting
    │   ├── similarity_service.py    # Embeddings & plagiarism
    │   └── grading_service.py       # LangChain scoring
    ├── utils/
    │   └── file_helpers.py   # PDF to image conversion
    └── uploads/              # Local storage for files

**[Click here to watch the video demonstration (Google Drive)](https://drive.google.com/file/d/1WNSPTo_mxf5nD0VzGS7AlrvCaHEVBSTw/view?usp=sharing)**
