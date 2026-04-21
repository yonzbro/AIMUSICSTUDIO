from fastapi import FastAPI
from pydantic import BaseModel
from model_loader import load_model, generate_lyrics_from_model, is_model_loaded, MODEL_NAME

app = FastAPI(title="Lyrics Generator API")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model-status")
async def model_status():
    return {
        "loaded": is_model_loaded(),
        "model_name": MODEL_NAME,
        "description": "Qwen2-1.5B for lyrics generation",
    }

@app.post("/load-model")
def trigger_load():
    load_model()
    return {"status": "loaded", "model_name": MODEL_NAME}

class LyricsRequest(BaseModel):
    prompt: str

@app.post("/generate-lyrics")
def generate_lyrics(request: LyricsRequest):
    lyrics = generate_lyrics_from_model(request.prompt)
    return {"lyrics": lyrics}
