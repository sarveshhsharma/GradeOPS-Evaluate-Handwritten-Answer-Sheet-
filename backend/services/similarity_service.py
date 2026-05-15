from sentence_transformers import SentenceTransformer, util
import torch
# Load the lightweight model globally
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Could not load embedding model. {e}")
    embedding_model = None

# Plagiarism threshold (85% similarity is usually a strong indicator for distinct logic structures)
SIMILARITY_THRESHOLD = 0.85

def check_similarity(new_answer: str, existing_answers: list[str]) -> bool:
    """
    Compares a new answer against a list of existing answers for the same question.
    Returns True if a highly similar answer (potential plagiarism) is found.
    """
    if not embedding_model or not existing_answers or not new_answer.strip():
        return False
        
    try:
        # Encode the target answer
        new_embedding = embedding_model.encode(new_answer, convert_to_tensor=True)
        
        # Encode all previous answers for this specific question
        existing_embeddings = embedding_model.encode(existing_answers, convert_to_tensor=True)
        
        # Compute cosine similarities between the new answer and all existing ones
        cosine_scores = util.cos_sim(new_embedding, existing_embeddings)[0]
        
        # Check if the highest score breaches our threshold
        max_score = torch.max(cosine_scores).item()
        
        if max_score >= SIMILARITY_THRESHOLD:
            return True
            
        return False
        
    except Exception as e:
        print(f"Similarity check failed: {e}")
        return False
    

def calculate_rubric_similarity(student_answer: str, correct_answer: str) -> float:
    """
    Calculates the semantic similarity between the student's answer and the strict rubric.
    Returns a percentage (0.0 to 100.0).
    """
    if not embedding_model or not student_answer.strip() or not correct_answer.strip():
        return 0.0
        
    try:
        # Encode both answers into vectors
        student_embedding = embedding_model.encode(student_answer, convert_to_tensor=True)
        rubric_embedding = embedding_model.encode(correct_answer, convert_to_tensor=True)
        
        # Calculate Cosine Similarity
        cosine_score = util.cos_sim(student_embedding, rubric_embedding)[0][0].item()
        
        # Convert to percentage and cap between 0 and 100
        percentage = max(0.0, min(100.0, cosine_score * 100))
        return round(percentage, 1)
        
    except Exception as e:
        print(f"Rubric similarity check failed: {e}")
        return 0.0