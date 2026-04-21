from fastapi import FastAPI
from pydantic import BaseModel
import os
from model_loader import load_model, generate_voice_from_text, is_model_loaded

app = FastAPI(title="Voice Generator API")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model-status")
async def model_status():
    return {
        "loaded": is_model_loaded(),
        "model_name": "gTTS (Google Text-to-Speech)",
        "description": "Text-to-Speech via Google TTS API",
    }

@app.post("/load-model")
async def trigger_load():
    load_model()
    return {"status": "loaded", "model_name": "gTTS"}

class VoiceRequest(BaseModel):
    text: str

@app.post("/generate-voice")
async def generate_voice(request: VoiceRequest):
    filename = f"voice_{abs(hash(request.text))}.wav"
    output_path = os.path.join(OUTPUT_DIR, filename)
    generate_voice_from_text(request.text, output_path)
    return {"voice_file": filename}
