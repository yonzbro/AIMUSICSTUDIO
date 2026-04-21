from fastapi import FastAPI, UploadFile, File
import os
from model_loader import load_model, split_audio, is_model_loaded

app = FastAPI(title="Remix Service API")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model-status")
async def model_status():
    return {
        "loaded": is_model_loaded(),
        "model_name": "Demucs htdemucs",
        "description": "Audio source separation (vocals, drums, bass, other)",
    }

@app.post("/load-model")
def trigger_load():
    load_model()
    return {"status": "loaded", "model_name": "Demucs htdemucs"}

@app.post("/remix")
def remix(file: UploadFile = File(...)):
    # Read contents synchronously since we are in a def handler (FastAPI handles it)
    contents = file.file.read() 
    temp_path = os.path.join(OUTPUT_DIR, f"remix_input_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(contents)

    stems = split_audio(temp_path, OUTPUT_DIR)
    return {"stems": stems}
