from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Antigravity Gateway API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
OUTPUT_DIR = "/app/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

LYRICS_URL = os.getenv("LYRICS_SERVICE_URL", "http://localhost:8001")
MUSIC_URL = os.getenv("MUSIC_SERVICE_URL", "http://localhost:8002")
VOICE_URL = os.getenv("VOICE_SERVICE_URL", "http://localhost:8003")
CLONE_URL = os.getenv("CLONE_SERVICE_URL", "http://localhost:8004")
REMIX_URL = os.getenv("REMIX_SERVICE_URL", "http://localhost:8005")

class SongRequest(BaseModel):
    prompt: str
    style: str

@app.post("/generate-song")
async def generate_song(request: SongRequest):
    # This is a conceptual pipeline orchestrating the microservices.
    async with httpx.AsyncClient() as client:
        # 1. Generate Lyrics
        try:
            lyrics_resp = await client.post(f"{LYRICS_URL}/generate-lyrics", json={"prompt": request.prompt})
            lyrics = lyrics_resp.json().get("lyrics", "Default lyrics")
        except:
            lyrics = "Default lyrics generated as fallback"
            
        # 2. Generate Music
        try:
            music_resp = await client.post(f"{MUSIC_URL}/generate-music", json={"prompt": f"{request.style} {request.prompt}", "duration": 5})
            music_file = music_resp.json().get("audio_url", "music.wav")
        except:
            music_file = "fallback_music.wav"
            
        # 3. Generate Voice
        try:
            voice_resp = await client.post(f"{VOICE_URL}/generate-voice", json={"text": lyrics})
            voice_file = voice_resp.json().get("voice_file", "voice.wav")
        except:
            voice_file = "fallback_voice.wav"
            
        # 4. Merge Audio (Using ffmpeg logic)
        final_song = f"final_song_{hash(request.prompt)}.wav"
        final_song_path = f"/app/outputs/{final_song}"
        
        music_path = f"/app/outputs/{music_file}"
        voice_path = f"/app/outputs/{voice_file}"
        
        import subprocess
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", voice_path,
                "-i", music_path,
                "-filter_complex", "amix=inputs=2:duration=longest",
                final_song_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print("FFmpeg merge failed:", e)
            final_song = "fallback_merged_song.wav"
        
    return {
        "status": "success",
        "lyrics": lyrics,
        "music_file": music_file,
        "voice_file": voice_file,
        "final_song": final_song
    }
