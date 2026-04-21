from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import os
import asyncio
import hashlib

app = FastAPI(title="Antigravity Gateway API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "/app/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# ── Service URLs ─────────────────────────────────────────────────
SERVICES = {
    "lyrics":  os.getenv("LYRICS_SERVICE_URL", "http://localhost:8001"),
    "music":   os.getenv("MUSIC_SERVICE_URL",  "http://localhost:8002"),
    "voice":   os.getenv("VOICE_SERVICE_URL",  "http://localhost:8003"),
    "clone":   os.getenv("CLONE_SERVICE_URL",  "http://localhost:8004"),
    "remix":   os.getenv("REMIX_SERVICE_URL",  "http://localhost:8005"),
}

# ── Models ───────────────────────────────────────────────────────
class PipelineRequest(BaseModel):
    prompt: str
    style: str
    features: list[str] = ["lyrics", "music", "voice"]  # default pipeline

class RemixRequest(BaseModel):
    pass  # file comes via multipart

# ── Health ───────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}

# ── Service Status (checks all services) ─────────────────────────
@app.get("/services/status")
async def services_status():
    """Check health and model status of every microservice."""
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICES.items():
            try:
                health_resp = await client.get(f"{url}/health")
                alive = health_resp.status_code == 200
            except Exception:
                alive = False

            model_loaded = False
            model_name = ""
            if alive:
                try:
                    model_resp = await client.get(f"{url}/model-status")
                    if model_resp.status_code == 200:
                        data = model_resp.json()
                        model_loaded = data.get("loaded", False)
                        model_name = data.get("model_name", "")
                except Exception:
                    pass

            results[name] = {
                "alive": alive,
                "model_loaded": model_loaded,
                "model_name": model_name,
                "url": url,
            }
    return results

# ── Trigger Model Load on a Specific Service ─────────────────────
@app.post("/services/{service_name}/load-model")
async def load_service_model(service_name: str):
    """Ask a specific service to download/load its AI model."""
    if service_name not in SERVICES:
        return {"error": f"Unknown service: {service_name}"}

    # 10 minutes timeout for model loading
    async with httpx.AsyncClient(timeout=600.0) as client:
        try:
            resp = await client.post(f"{url}/load-model")
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

# ── FFmpeg Merge (async) ─────────────────────────────────────────
async def _merge_audio(voice_path: str, music_path: str, output_path: str) -> None:
    process = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest:normalize=0",
        "-ar", "22050",
        output_path,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    rc = await process.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg exited with code {rc}")

# ── Main Pipeline (parallel) ─────────────────────────────────────
@app.post("/generate-song")
async def generate_song(request: PipelineRequest):
    features = [f.lower().strip() for f in request.features]

    # 10 minutes timeout for song generation pipeline
    async with httpx.AsyncClient(timeout=600.0) as client:

        # ── Build parallel tasks based on selected features ──
        async def _lyrics() -> str:
            try:
                r = await client.post(
                    f"{SERVICES['lyrics']}/generate-lyrics",
                    json={"prompt": request.prompt},
                )
                return r.json().get("lyrics", "")
            except Exception as e:
                print(f"Lyrics failed: {e}")
                return "Lyrics generation unavailable."

        async def _music() -> str:
            try:
                r = await client.post(
                    f"{SERVICES['music']}/generate-music",
                    json={"prompt": f"{request.style} {request.prompt}", "duration": 10},
                )
                return r.json().get("audio_url", "")
            except Exception as e:
                print(f"Music failed: {e}")
                return ""

        async def _voice(lyrics_text: str) -> str:
            try:
                r = await client.post(
                    f"{SERVICES['voice']}/generate-voice",
                    json={"text": lyrics_text},
                )
                return r.json().get("voice_file", "")
            except Exception as e:
                print(f"Voice failed: {e}")
                return ""

        # ── Phase 1: Lyrics (needed before voice) ──
        lyrics = ""
        if "lyrics" in features or "voice" in features:
            lyrics = await _lyrics()

        # ── Phase 2: Music + Voice in parallel ──
        parallel_tasks = {}
        if "music" in features:
            parallel_tasks["music"] = _music()
        if "voice" in features:
            parallel_tasks["voice"] = _voice(lyrics)

        parallel_results = {}
        if parallel_tasks:
            keys = list(parallel_tasks.keys())
            values = await asyncio.gather(*parallel_tasks.values())
            parallel_results = dict(zip(keys, values))

        music_file = parallel_results.get("music", "")
        voice_file = parallel_results.get("voice", "")

        # ── Phase 3: Merge if both music and voice exist ──
        final_song = ""
        prompt_hash = hashlib.md5(request.prompt.encode()).hexdigest()[:10]

        if music_file and voice_file:
            music_path = f"{OUTPUT_DIR}/{os.path.basename(music_file)}"
            voice_path = f"{OUTPUT_DIR}/{os.path.basename(voice_file)}"
            final_song = f"final_{prompt_hash}.wav"
            final_path = f"{OUTPUT_DIR}/{final_song}"

            try:
                await _merge_audio(voice_path, music_path, final_path)
                print(f"Merged: {final_song}")
            except Exception as e:
                print(f"Merge failed: {e}")
                final_song = os.path.basename(voice_file) if voice_file else os.path.basename(music_file)
        elif music_file:
            final_song = os.path.basename(music_file)
        elif voice_file:
            final_song = os.path.basename(voice_file)

    return {
        "status": "success",
        "features_used": features,
        "lyrics": lyrics,
        "music_file": music_file,
        "voice_file": voice_file,
        "final_song": final_song,
    }

# ── Remix Endpoint (proxy to remix-service) ──────────────────────
@app.post("/remix")
async def remix_audio(file: UploadFile = File(...)):
    """Upload audio → Demucs stem separation."""
    contents = await file.read()

    # 10 minutes timeout for remixing (stem separation)
    async with httpx.AsyncClient(timeout=600.0) as client:
        try:
            resp = await client.post(
                f"{SERVICES['remix']}/remix",
                files={"file": (file.filename, contents, file.content_type or "audio/wav")},
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
