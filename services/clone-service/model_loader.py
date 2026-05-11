"""
Voice Profile Manager — Clone Service
Manages uploaded voice samples as reusable profiles for XTTS-v2 cloning.
"""

import os
import uuid
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

PROFILES_DIR = os.getenv("PROFILES_DIR", "/app/voice_profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

# Minimum voice sample duration in seconds
MIN_DURATION_SEC = 3
# Target format for XTTS-v2 compatibility
TARGET_SAMPLE_RATE = 22050
TARGET_CHANNELS = 1


def _get_audio_info(path: str) -> dict:
    """Use ffprobe to get audio file metadata."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return {}
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[Clone] ffprobe error: {e}")
        return {}


def _validate_and_convert(input_path: str, output_path: str) -> dict:
    """
    Validate audio file and convert to XTTS-v2 compatible format.
    Returns metadata dict with duration, sample_rate, etc.
    """
    info = _get_audio_info(input_path)
    if not info:
        raise ValueError("Could not read audio file. Is it a valid audio format?")

    # Extract duration
    duration = 0.0
    if "format" in info and "duration" in info["format"]:
        duration = float(info["format"]["duration"])
    elif "streams" in info:
        for stream in info["streams"]:
            if "duration" in stream:
                duration = max(duration, float(stream["duration"]))

    if duration < MIN_DURATION_SEC:
        raise ValueError(
            f"Voice sample too short: {duration:.1f}s "
            f"(minimum {MIN_DURATION_SEC}s required)"
        )

    # Convert to XTTS-v2 compatible format:
    # 22050 Hz, mono, 16-bit PCM WAV
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", input_path,
                "-ar", str(TARGET_SAMPLE_RATE),
                "-ac", str(TARGET_CHANNELS),
                "-acodec", "pcm_s16le",
                "-t", "30",  # Cap at 30 seconds max
                output_path,
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Audio conversion timed out.")

    # Get final info
    final_info = _get_audio_info(output_path)
    final_duration = float(final_info.get("format", {}).get("duration", duration))

    return {
        "original_duration": round(duration, 2),
        "processed_duration": round(final_duration, 2),
        "sample_rate": TARGET_SAMPLE_RATE,
        "channels": TARGET_CHANNELS,
    }


def save_voice_profile(audio_path: str, display_name: str = "") -> dict:
    """
    Process and save a voice sample as a reusable profile.
    Returns profile metadata.
    """
    profile_id = f"vp_{uuid.uuid4().hex[:10]}"
    profile_dir = os.path.join(PROFILES_DIR, profile_id)
    os.makedirs(profile_dir, exist_ok=True)

    wav_path = os.path.join(profile_dir, "reference.wav")

    try:
        audio_meta = _validate_and_convert(audio_path, wav_path)
    except Exception:
        # Clean up on failure
        shutil.rmtree(profile_dir, ignore_errors=True)
        raise

    # Save profile metadata
    metadata = {
        "profile_id": profile_id,
        "display_name": display_name or f"Voice {profile_id[-6:]}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "audio": audio_meta,
        "wav_path": wav_path,
    }

    meta_path = os.path.join(profile_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Clone] Voice profile saved: {profile_id}")
    return metadata


def list_profiles() -> list[dict]:
    """List all saved voice profiles."""
    profiles = []
    for entry in sorted(Path(PROFILES_DIR).iterdir()):
        meta_path = entry / "metadata.json"
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    profiles.append(json.load(f))
            except Exception as e:
                print(f"[Clone] Skipping corrupt profile {entry.name}: {e}")
    return profiles


def get_profile(profile_id: str) -> dict | None:
    """Get a specific profile's metadata."""
    meta_path = os.path.join(PROFILES_DIR, profile_id, "metadata.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path) as f:
        return json.load(f)


def get_profile_wav_path(profile_id: str) -> str | None:
    """Get the WAV file path for a profile (for XTTS-v2 speaker_wav)."""
    wav_path = os.path.join(PROFILES_DIR, profile_id, "reference.wav")
    return wav_path if os.path.exists(wav_path) else None


def delete_profile(profile_id: str) -> bool:
    """Delete a voice profile and its files."""
    profile_dir = os.path.join(PROFILES_DIR, profile_id)
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
        print(f"[Clone] Profile deleted: {profile_id}")
        return True
    return False


# ── Service status ────────────────────────────────────────────────

def is_model_loaded() -> bool:
    """Clone service is always ready (no ML model needed)."""
    return True


def load_model():
    """No model to load — clone service manages voice profiles."""
    print("[Clone] Voice Profile Manager ready.")
    print(f"[Clone] Profiles directory: {PROFILES_DIR}")
    print(f"[Clone] Existing profiles: {len(list_profiles())}")
