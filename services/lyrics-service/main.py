from fastapi import FastAPI
from pydantic import BaseModel
from model_loader import load_model, generate_lyrics_from_model

app = FastAPI(title="Lyrics Generator API")

class LyricsRequest(BaseModel):
    prompt: str

@app.on_event("startup")
async def startup_event():
    load_model()

@app.post("/generate-lyrics")
async def generate_lyrics(request: LyricsRequest):
    lyrics = generate_lyrics_from_model(request.prompt)
    return {"lyrics": lyrics}
