from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from generator import MusicGenerator
from model_loader import get_model_loader
import os

app = FastAPI(title="AI Music Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

generator = MusicGenerator()
loader = get_model_loader()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model-status")
async def model_status():
    return {
        "loaded": loader._is_loaded,
        "model_name": "facebook/musicgen-small",
        "description": "MusicGen for instrumental music generation",
    }

@app.post("/load-model")
def trigger_load():
    loader.load()
    return {"status": "loaded", "model_name": "facebook/musicgen-small"}

class MusicRequest(BaseModel):
    prompt: str
    duration: int = 10

class MusicResponse(BaseModel):
    audio_url: str

@app.post("/generate-music", response_model=MusicResponse)
def generate_music(request: MusicRequest):
    filename = generator.generate(request.prompt, request.duration)
    return {"audio_url": f"/outputs/{filename}"}
