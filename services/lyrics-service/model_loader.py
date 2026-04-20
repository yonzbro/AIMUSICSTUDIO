import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gc

_model = None
_tokenizer = None
MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"

def load_model():
    global _model, _tokenizer
    if _model is None:
        print(f"Loading {MODEL_NAME}...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        # Use float32 on CPU (float16 is not reliable on CPU),
        # float16 only on GPU
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
    global _model, _tokenizer
    if _model is None:
        load_model()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
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

        text = _tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = _tokenizer([text], return_tensors="pt").to(device)

        print("Generating lyrics...")
        generated_ids = _model.generate(
            model_inputs.input_ids,
            max_new_tokens=200,
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
            print("Clearing VRAM Cache...")
            torch.cuda.empty_cache()
        gc.collect()
