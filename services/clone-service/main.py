"""
Clone Service API — Voice Profile Management
Upload, validate, store, and manage voice profiles for AI voice cloning.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import tempfile
from model_loader import (
    load_model,
    is_model_loaded,
    save_voice_profile,
    list_profiles,
    get_profile,
    get_profile_wav_path,
    delete_profile,
)

app = FastAPI(title="Voice Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROFILES_DIR = os.getenv("PROFILES_DIR", "/app/voice_profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

# Serve profile audio files for preview/playback
app.mount("/voice_profiles", StaticFiles(directory=PROFILES_DIR), name="voice_profiles")


# ── Health & Status ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/model-status")
async def model_status():
    profiles = list_profiles()
    return {
        "loaded": is_model_loaded(),
        "model_name": "Voice Profile Manager",
        "description": "Upload voice samples → create reusable voice profiles for AI cloning",
        "total_profiles": len(profiles),
    }


@app.post("/load-model")
async def trigger_load():
    load_model()
    return {"status": "loaded", "model_name": "Voice Profile Manager"}


# ── Upload & Clone ───────────────────────────────────────────────

@app.post("/clone-voice")
async def clone_voice(
    file: UploadFile = File(...),
    display_name: str = Form(default=""),
):
    """
    Upload a voice sample → validate → convert → save as a reusable voice profile.

    The uploaded audio is:
    1. Validated (min 3 seconds, valid audio format)
    2. Converted to XTTS-v2 compatible format (22050Hz, mono, PCM WAV)
    3. Stored as a named profile that can be used for AI voice cloning

    Returns the profile metadata including the profile_id.
    """
    # Save uploaded file to temp location
    suffix = os.path.splitext(file.filename or "upload.wav")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        profile = save_voice_profile(tmp_path, display_name=display_name)
        return {
            "status": "success",
            "voice_profile_id": profile["profile_id"],
            "display_name": profile["display_name"],
            "audio": profile["audio"],
            "created_at": profile["created_at"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── Profiles CRUD ────────────────────────────────────────────────

@app.get("/profiles")
async def get_all_profiles():
    """List all saved voice profiles."""
    profiles = list_profiles()
    return {"profiles": profiles, "total": len(profiles)}


@app.get("/profiles/{profile_id}")
async def get_profile_detail(profile_id: str):
    """Get details of a specific voice profile."""
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")
    return profile


@app.get("/profiles/{profile_id}/wav-path")
async def get_profile_wav(profile_id: str):
    """
    Get the WAV file path for a profile.
    Used internally by voice-service to get the speaker_wav path.
    """
    wav_path = get_profile_wav_path(profile_id)
    if not wav_path:
        raise HTTPException(status_code=404, detail=f"WAV not found for profile '{profile_id}'")
    return {"profile_id": profile_id, "wav_path": wav_path}


@app.delete("/profiles/{profile_id}")
async def remove_profile(profile_id: str):
    """Delete a voice profile and its files."""
    deleted = delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")
    return {"status": "deleted", "profile_id": profile_id}
