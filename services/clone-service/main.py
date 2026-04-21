from fastapi import FastAPI, UploadFile, File
import os
from model_loader import load_model, extract_voice_embedding, is_model_loaded
import uuid

app = FastAPI(title="Voice Clone API")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model-status")
async def model_status():
    return {
        "loaded": is_model_loaded(),
        "model_name": "OpenVoice (stub)",
        "description": "Voice cloning via speaker embedding extraction",
    }

@app.post("/load-model")
async def trigger_load():
    load_model()
    return {"status": "loaded", "model_name": "OpenVoice (stub)"}

@app.post("/clone-voice")
async def clone_voice(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_path = os.path.join(OUTPUT_DIR, f"temp_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    voice_profile_id = f"user_{uuid.uuid4().hex[:8]}"

    # Process it
    extract_voice_embedding(temp_path, voice_profile_id)

    return {"voice_profile_id": voice_profile_id}
