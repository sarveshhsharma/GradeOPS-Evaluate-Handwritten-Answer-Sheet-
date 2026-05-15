from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from services.shared_llm import shared_llm as llm  # Import the shared model
import json


class GradingResult(BaseModel):
    score_awarded: float = Field(description="The numeric score awarded to the student.")
    justification: str = Field(description="A brief explanation of why this score was awarded.")
    deductions: str = Field(description="Specific reasons for marks deducted. Write 'None' if full marks.")

parser = PydanticOutputParser(pydantic_object=GradingResult)

def evaluate_answer(student_answer: str, correct_answer: str, max_marks: float) -> dict:
    # We use a Few-Shot approach by providing examples of perfect and partial grading
    prompt = PromptTemplate(
        template="""<|im_start|>system
        You are a strict but fair university grader. Evaluate the student's answer based ONLY on the provided correct answer rubric. 
        
        {format_instructions}

        === EXAMPLES OF GRADING ===
        
        Example 1 (Perfect Score):
        Max Marks Possible: 5.0
        Correct Answer / Rubric: Mitochondria is the powerhouse of the cell, responsible for generating ATP through cellular respiration.
        Student's Answer: The mitochondria creates energy for the cell by producing ATP via cellular respiration. It's often called the powerhouse.
        Output:
        ```json
        {{
            "score_awarded": 5.0,
            "justification": "The student correctly identified the function of mitochondria, including ATP production and cellular respiration.",
            "deductions": "None"
        }}
        ```

        Example 2 (Partial Score):
        Max Marks Possible: 5.0
        Correct Answer / Rubric: Mitochondria is the powerhouse of the cell, responsible for generating ATP through cellular respiration.
        Student's Answer: Mitochondria is the powerhouse of the cell.
        Output:
        ```json
        {{
            "score_awarded": 2.5,
            "justification": "The student identified the basic analogy but failed to mention ATP or cellular respiration.",
            "deductions": "Deducted 2.5 marks for missing the scientific mechanism (ATP and cellular respiration)."
        }}
        ```
        ===========================
        <|im_end|>
        <|im_start|>user
        Max Marks Possible: {max_marks}
        Correct Answer / Rubric: {correct_answer}
        Student's Answer: {student_answer}
        <|im_end|>
        <|im_start|>assistant
        """,
        input_variables=["max_marks", "correct_answer", "student_answer"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm
    
    try:
        # 1. Ask the LLM to generate the grade
        response = chain.invoke({
            "max_marks": max_marks,
            "correct_answer": correct_answer,
            "student_answer": student_answer
        })
        
        # 2. Try Langchain's strict Pydantic parsing first
        try:
            result = parser.parse(response)
            return result.model_dump()
            
        except Exception as parse_err:
            # 3. FALLBACK: If Langchain fails, manually clean and extract the JSON
            print(f"⚠️ Strict parsing failed, attempting manual rescue... ")
            
            # Strip out markdown formatting that confuses the parser
            clean_text = response.replace("```json", "").replace("```", "").strip()
            
            # Find where the JSON actually starts and ends in case the LLM was chatty
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = clean_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                print("✅ Manual rescue successful!")
                return {
                    "score_awarded": float(data.get("score_awarded", 0.0)),
                    "justification": str(data.get("justification", "Graded successfully, but justification formatting was rescued.")),
                    "deductions": str(data.get("deductions", "None"))
                }
            else:
                raise ValueError("No valid JSON brackets found in the LLM response.")

    except Exception as e:
        print(f"❌ Local grading completely failed: {e}")
        # Print the exact raw response so you can see what the LLM did wrong in the terminal
        print(f"RAW LLM RESPONSE WAS: {response}") 
        return {
            "score_awarded": 0.0,
            "justification": "AI Grading failed to process due to local model parsing error.",
            "deductions": "System Error."
        }