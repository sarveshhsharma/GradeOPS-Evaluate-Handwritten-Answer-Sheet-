import json
from langchain_core.prompts import PromptTemplate
from services.shared_llm import shared_llm as llm  # Import the shared model

def segment_answers(raw_text: str) -> dict:
    prompt = PromptTemplate.from_template(
            """<|im_start|>system
            You are an assistant parsing extracted text from a student's exam.
            Output ONLY a valid JSON object where the keys are the integer question numbers, and the values are the student's text. 
            
            CRITICAL RULE: You are a pure text-extraction pipeline. You MUST copy the student's exact text word-for-word. If a student's answer contains multiple sub-parts, lists, paragraphs, or letters (e.g., (a), (b), (c)), you MUST capture ALL of them and combine them into a single continuous string for that question number. 
            DO NOT SUMMARIZE. DO NOT TRUNCATE. If you stop extracting before the end of the student's text, the system will fail.            
            Do not add any conversational text.
            <|im_end|>
            <|im_start|>user
            Raw OCR Text:
            {raw_text}
            <|im_end|>
            <|im_start|>assistant
            """
    )
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({"raw_text": raw_text})
        clean_text = response.replace("```json", "").replace("```", "").strip()
        segmented_dict = json.loads(clean_text)
        
        return {int(k): str(v) for k, v in segmented_dict.items() if k.isdigit()}
    except Exception as e:
        print(f"Failed to segment text locally: {e}")
        return {}