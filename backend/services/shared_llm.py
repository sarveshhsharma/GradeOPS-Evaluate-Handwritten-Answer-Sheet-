import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

print("Loading shared local text model to save RAM...")
device = "mps" if torch.backends.mps.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(device)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=4096,
    temperature=0.1,
    return_full_text=False
)

# This single instance will be shared across your app
shared_llm = HuggingFacePipeline(pipeline=pipe)