from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from generator import MusicGenerator
import os

app = FastAPI(title="AI Music Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

class MusicRequest(BaseModel):
    prompt: str
    duration: int = 10

class MusicResponse(BaseModel):
    audio_url: str

generator = MusicGenerator()

@app.post("/generate-music", response_model=MusicResponse)
def generate_music(request: MusicRequest):
    filename = generator.generate(request.prompt, request.duration)
    return {"audio_url": f"/outputs/{filename}"}
