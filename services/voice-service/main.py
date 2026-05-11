from fastapi import FastAPI
from pydantic import BaseModel
import os
from model_loader import load_model, generate_voice_from_text, is_model_loaded, SUPPORTED_LANGUAGES

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
        "model_name": "Coqui XTTS-v2 (Multilingual + Voice Cloning)",
        "description": "17-language expressive TTS with voice cloning support — local inference, no internet required",
        "supported_languages": sorted(SUPPORTED_LANGUAGES),
    }


@app.post("/load-model")
async def trigger_load():
    load_model()
    return {"status": "loaded", "model_name": "Coqui XTTS-v2"}


class VoiceRequest(BaseModel):
    text: str
    language: str = "tr"                         # Default: Turkish
    voice_profile_id: str | None = None          # Optional: use cloned voice


@app.post("/generate-voice")
async def generate_voice(request: VoiceRequest):
    filename = f"voice_{abs(hash(request.text + request.language))}.wav"
    output_path = os.path.join(OUTPUT_DIR, filename)

    generate_voice_from_text(
        text=request.text,
        output_path=output_path,
        language=request.language,
        voice_profile_id=request.voice_profile_id,
    )

    return {"voice_file": filename}
