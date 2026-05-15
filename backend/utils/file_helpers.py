import os
import uuid
import shutil
from fastapi import UploadFile
from pdf2image import convert_from_path
from typing import List

# Define storage directories
BASE_UPLOAD_DIR = "uploads"
FILES_DIR = os.path.join(BASE_UPLOAD_DIR, "files")
IMAGE_DIR = os.path.join(BASE_UPLOAD_DIR, "images")

# Ensure directories exist when the app starts
os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

def save_uploaded_file(file: UploadFile) -> str:
    """
    Saves ANY uploaded file (PDF, JPG, PNG) to the local filesystem with a unique UUID.
    Returns the file path.
    """
    # Generate a unique filename to prevent overwriting
    file_extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(FILES_DIR, unique_filename)

    # Write the file to disk in chunks to avoid memory issues
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path

def convert_pdf_to_images(pdf_path: str) -> List[str]:
    """
    Converts a saved PDF into a list of JPEG images (one per page).
    Returns a list of file paths to the generated images.
    """
    base_name = os.path.basename(pdf_path).split(".")[0]
    submission_image_dir = os.path.join(IMAGE_DIR, base_name)
    os.makedirs(submission_image_dir, exist_ok=True)

    # Convert PDF to images (100 DPI is web-standard and processes fast)
    pages = convert_from_path(pdf_path, dpi=100)
    
    image_paths = []
    for i, page in enumerate(pages):
        image_filename = f"page_{i + 1}.jpg"
        image_path = os.path.join(submission_image_dir, image_filename)
        page.save(image_path, "JPEG")
        image_paths.append(image_path)

    return image_paths