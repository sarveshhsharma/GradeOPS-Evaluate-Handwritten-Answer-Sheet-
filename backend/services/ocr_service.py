import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

# ============================================================================
# MODEL LOADING (Loads once on startup to save RAM)
# Switched to 3B model since we are running unquantized on macOS
# ============================================================================
MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct" 

try:
    # Detect Apple Silicon (M1/M2/M3) for hardware acceleration, fallback to CPU
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    
    print(f"Loading Vision Model on device: {device}...")
    
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID, 
        torch_dtype=torch.float16, # Force half-precision to save ~2GB of RAM
        device_map="auto" 
    )
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    MODEL_LOADED = True
    print("Vision Model loaded successfully.")
except Exception as e:
    print(f"Warning: Failed to load Qwen2.5-VL. {e}")
    MODEL_LOADED = False

def extract_text_from_image(image_path: str) -> str:
    """
    Uses Qwen2.5-VL to read handwriting from an exam image.
    """
    if not MODEL_LOADED:
        return "Model not loaded. Please check your RAM/VRAM."

    messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image", 
                        "image": f"file://{image_path}",
                        "max_pixels": 250880  # Much smaller chunk size for the Mac
                    },
                    {"type": "text", "text": "Transcribe all the handwritten text in this image exactly as written. Ensure you include any question numbers (e.g., 'Ans 1', 'Q2'). Do not add any extra commentary."}
                ]
            }
        ]

    # Prepare inputs
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt"
    ).to(device)

    # Generate output
    generated_ids = model.generate(**inputs, max_new_tokens=2048)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    
    return output_text[0]