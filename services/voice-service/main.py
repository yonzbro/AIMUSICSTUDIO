from fastapi import FastAPI
from pydantic import BaseModel
import os
from model_loader import load_model, generate_voice_from_text

app = FastAPI(title="Voice Generator API")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class VoiceRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup_event():
    load_model()

@app.post("/generate-voice")
async def generate_voice(request: VoiceRequest):
    filename = f"voice_{hash(request.text)}.wav"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    generate_voice_from_text(request.text, output_path)
    
    return {"voice_file": filename}
