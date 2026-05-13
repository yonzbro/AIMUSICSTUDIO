from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import os
import asyncio
import hashlib
from prompt_enhancer import enhance_prompt, generate_song_title, detect_genre

app = FastAPI(title="Sıcumaı Gateway API")

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
    "rvc":     os.getenv("RVC_SERVICE_URL",    "http://localhost:8006"),
}

# ── Models ───────────────────────────────────────────────────────
class PipelineRequest(BaseModel):
    prompt: str
    style: str
    language: str = "tr"                              # default: Turkish
    features: list[str] = ["lyrics", "music", "voice"]  # default pipeline
    enhance_prompt: bool = True                       # AI prompt enhancement
    voice_profile_id: str | None = None               # optional: cloned voice
    use_rvc: bool = True                              # Use RVC for high-quality singing if profile exists
    rvc_pitch: int = 0                                # RVC pitch shift
    rvc_index_rate: float = 0.75                      # RVC index rate (cloning strength)
    # Audio effect parameters
    echo_delay: float = 60.0                          # ms
    echo_decay: float = 0.4
    vocal_volume: float = 1.5
    music_volume: float = 0.8

class EnhanceRequest(BaseModel):
    prompt: str
    style: str = ""
    language: str = "en"

class RemixRequest(BaseModel):
    pass  # file comes via multipart

# ── Health ───────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0"}

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
            resp = await client.post(f"{SERVICES[service_name]}/load-model")
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

# ── Warmup: Load All Models ──────────────────────────────────────
@app.post("/warmup")
async def warmup_all():
    """
    Trigger all services to load their AI models in parallel.
    Call this once after docker-compose up to pre-warm the pipeline.
    """
    results = {}

    async def _load(name: str, url: str):
        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                resp = await client.post(f"{url}/load-model")
                return name, resp.json()
        except Exception as e:
            return name, {"error": str(e)}

    tasks = [_load(name, url) for name, url in SERVICES.items()]
    for coro in asyncio.as_completed(tasks):
        name, result = await coro
        results[name] = result
        print(f"[Warmup] {name}: {result}")

    return {"status": "warmup_complete", "results": results}

# ── AI Prompt Enhancement ────────────────────────────────────────
@app.post("/enhance-prompt")
async def enhance_prompt_endpoint(request: EnhanceRequest):
    """
    Use Qwen2 AI to enhance a short prompt into a detailed music production prompt.
    Also generates a song title and detects genre.
    """
    enhanced, title, genre = await asyncio.gather(
        enhance_prompt(request.prompt, request.style, request.language),
        generate_song_title(request.prompt, request.style),
        detect_genre(request.prompt),
    )

    return {
        "original_prompt": request.prompt,
        "enhanced_prompt": enhanced,
        "song_title": title,
        "detected_genre": genre,
    }

# ── Voice Profiles Proxy ─────────────────────────────────────────
@app.get("/voice-profiles")
async def list_voice_profiles():
    """List all available voice profiles from clone-service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{SERVICES['clone']}/profiles")
            return resp.json()
        except Exception as e:
            return {"profiles": [], "total": 0, "error": str(e)}

# ── Clone Voice Proxy ────────────────────────────────────────────
@app.post("/services/clone/clone-voice")
async def clone_voice_proxy(file: UploadFile = File(...)):
    """Proxy voice clone uploads to clone-service."""
    contents = await file.read()
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f"{SERVICES['clone']}/clone-voice",
                files={"file": (file.filename, contents, file.content_type or "audio/wav")},
            )
            
            if resp.status_code != 200:
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=resp.status_code, content=resp.json())
                
            return resp.json()
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))

# ── FFmpeg Merge (async) ─────────────────────────────────────────
async def _merge_audio(
    voice_path: str,
    music_path: str,
    output_path: str,
    echo_delay: float = 60.0,
    echo_decay: float = 0.4,
    vocal_volume: float = 1.5,
    music_volume: float = 0.8,
) -> None:
    """Merge voice and music with customizable studio effects."""
    # Build FFmpeg filter chain with user-customizable parameters
    filter_complex = (
        f"[0:a]aecho=0.8:0.88:{echo_delay}:{echo_decay},"
        f"volume={vocal_volume}[v];"
        f"[1:a]volume={music_volume}[m];"
        f"[v][m]amix=inputs=2:duration=shortest:dropout_transition=0"
    )

    process = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y",
        "-i", voice_path,
        "-stream_loop", "-1", "-i", music_path,
        "-filter_complex", filter_complex,
        "-c:a", "libmp3lame",
        "-b:a", "192k",
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

    # ── Phase 0: AI Prompt Enhancement (optional) ──
    enhanced_prompt = request.prompt
    song_title = ""

    if request.enhance_prompt:
        try:
            enhanced_prompt = await enhance_prompt(request.prompt, request.style, request.language)
            song_title = await generate_song_title(request.prompt, request.style)
            
            print(f"[Pipeline] Enhanced: '{request.prompt[:30]}' → '{enhanced_prompt[:50]}'")
            print(f"[Pipeline] Title: {song_title}")
        except Exception as e:
            print(f"[Pipeline] Enhancement failed, using original: {e}")
            enhanced_prompt = request.prompt
            song_title = request.prompt.split()[:3]
            song_title = " ".join(song_title).title() if isinstance(song_title, list) else song_title

    # 10 minutes timeout for song generation pipeline
    async with httpx.AsyncClient(timeout=600.0) as client:

        # ── Build parallel tasks based on selected features ──
        async def _lyrics() -> str:
            try:
                r = await client.post(
                    f"{SERVICES['lyrics']}/generate-lyrics",
                    json={"prompt": enhanced_prompt},
                )
                return r.json().get("lyrics", "")
            except Exception as e:
                print(f"Lyrics failed: {e}")
                return "Lyrics generation unavailable."

        async def _music() -> str:
            try:
                r = await client.post(
                    f"{SERVICES['music']}/generate-music",
                    json={"prompt": f"{request.style} {enhanced_prompt}", "duration": 8},
                )
                return r.json().get("audio_url", "")
            except Exception as e:
                print(f"Music failed: {e}")
                return ""

        async def _voice(lyrics_text: str) -> str:
            try:
                payload = {
                    "text": lyrics_text,
                    "language": request.language,
                }
                # Pass voice_profile_id if provided (for cloned voice)
                if request.voice_profile_id:
                    payload["voice_profile_id"] = request.voice_profile_id

                r = await client.post(
                    f"{SERVICES['voice']}/generate-voice",
                    json=payload,
                )
                return r.json().get("voice_file", "")
            except Exception as e:
                print(f"Voice failed: {e}")
                return ""

        async def _rvc(voice_file: str) -> str:
            """Convert TTS voice to high-quality RVC singing voice."""
            if not request.voice_profile_id:
                return voice_file
            
            try:
                print(f"[Pipeline] RVC: Converting {voice_file} using profile {request.voice_profile_id}...")
                r = await client.post(
                    f"{SERVICES['rvc']}/convert",
                    json={
                        "source_audio_path": voice_file,
                        "voice_profile_id": request.voice_profile_id,
                        "f0_up_key": request.rvc_pitch,
                        "index_rate": request.rvc_index_rate
                    },
                )
                res = r.json()
                if res.get("status") == "success":
                    return res.get("converted_file", voice_file)
                else:
                    print(f"RVC conversion failed: {res.get('detail')}")
                    return voice_file
            except Exception as e:
                print(f"RVC service failed: {e}")
                return voice_file

        # ── Phase 1: Lyrics ──
        lyrics = ""
        if "lyrics" in features or "voice" in features:
            lyrics = await _lyrics()

        # ── Phase 2: Music (Sequential) ──
        music_file = ""
        if "music" in features:
            music_file = await _music()

        # ── Phase 3: Voice (Sequential) ──
        voice_file = ""
        if "voice" in features:
            voice_file = await _voice(lyrics)

        # ── Phase 4: RVC Conversion (Sequential after Voice) ──
        if voice_file and request.voice_profile_id and request.use_rvc:
            voice_file = await _rvc(voice_file)

        # ── Phase 4: Merge if both music and voice exist ──
        final_song = ""
        prompt_hash = hashlib.md5(request.prompt.encode()).hexdigest()[:10]

        if music_file and voice_file:
            music_path = f"{OUTPUT_DIR}/{os.path.basename(music_file)}"
            voice_path = f"{OUTPUT_DIR}/{os.path.basename(voice_file)}"
            final_song = f"final_{prompt_hash}.mp3"
            final_path = f"{OUTPUT_DIR}/{final_song}"

            try:
                await _merge_audio(
                    voice_path, music_path, final_path,
                    echo_delay=request.echo_delay,
                    echo_decay=request.echo_decay,
                    vocal_volume=request.vocal_volume,
                    music_volume=request.music_volume,
                )
            except Exception as e:
                return {"status": "error", "message": f"Audio merge failed: {str(e)}"}
        elif music_file:
            final_song = os.path.basename(music_file)
        elif voice_file:
            final_song = os.path.basename(voice_file)
        else:
            return {"status": "error", "message": "Failed to generate any audio component (music/voice)."}

    return {
        "status": "success",
        "features_used": features,
        "lyrics": lyrics,
        "music_file": music_file,
        "voice_file": voice_file,
        "final_song": os.path.basename(final_song) if final_song else "",
        # ── New v2.0 fields ──
        "song_title": song_title,
        "enhanced_prompt": enhanced_prompt,
        "voice_profile_id": request.voice_profile_id,
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

app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")
