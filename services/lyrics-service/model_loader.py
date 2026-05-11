import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gc

import threading

_model = None
_tokenizer = None
_lock = threading.Lock()
MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"

def is_model_loaded() -> bool:
    return _model is not None

def load_model():
    global _model, _tokenizer
    if _model is None:
        print(f"Loading {MODEL_NAME}...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        # Use float16 on GPU for better performance and lower VRAM
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype,
            device_map=device,
            low_cpu_mem_usage=True
        )
        print(f"Model loaded to {device}.")

def generate_lyrics_from_model(prompt: str) -> str:
    """
    Generate text from a prompt using Qwen2.
    
    Supports two modes:
    1. Songwriting mode (default): standard lyrics generation
    2. Gateway AI mode: when prompt contains [SYSTEM]/[USER] tags,
       uses custom system/user messages (for prompt enhancement,
       title generation, genre detection, etc.)
    """
    global _model, _tokenizer
    if _model is None:
        load_model()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    with _lock:
        try:
            # ── Detect gateway AI mode ──
            if "[SYSTEM]" in prompt and "[USER]" in prompt:
                # Gateway prompt_enhancer sends structured prompts
                parts = prompt.split("[USER]")
                system_content = parts[0].replace("[SYSTEM]", "").strip()
                user_content = parts[1].strip() if len(parts) > 1 else prompt

                messages = [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content},
                ]
                max_tokens = 100  # Shorter output for AI tasks
                print(f"[Qwen2] Gateway AI mode: {system_content[:50]}...")
            else:
                # ── Standard songwriting mode ──
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a professional songwriter. Output ONLY the song lyrics "
                            "without any intro, outro, or conversational filler. "
                            "Include [Verse] and [Chorus] structure."
                        )
                    },
                    {"role": "user", "content": f"Write a song about: {prompt}"}
                ]
                max_tokens = 250
                print("[Qwen2] Songwriting mode")

            text = _tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = _tokenizer([text], return_tensors="pt").to(device)

            print(f"Generating on {device}...")
            generated_ids = _model.generate(
                model_inputs.input_ids,
                max_new_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
            )
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids
                in zip(model_inputs.input_ids, generated_ids)
            ]

            response = _tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response

        finally:
            if device == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
