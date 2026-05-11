import os
import torch
from TTS.api import TTS
import gc

_model: TTS | None = None
_ready = False

# Reference audio file path (generated at Docker build time via espeak-ng)
REFERENCE_WAV = os.getenv("REFERENCE_WAV", "/app/reference.wav")

# Voice profiles shared volume (managed by clone-service)
PROFILES_DIR = os.getenv("PROFILES_DIR", "/app/voice_profiles")

# Supported XTTS-v2 languages
SUPPORTED_LANGUAGES = {
    "tr", "en", "de", "fr", "es", "it", "pt", "pl",
    "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"
}

def is_model_loaded() -> bool:
    return _ready


def load_model():
    """Download (first run) and load Coqui XTTS-v2 onto GPU/CPU."""
    global _model, _ready

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[XTTS-v2] Loading model on {device}...")

    # CUDA performance optimization
    if device == "cuda":
        torch.backends.cudnn.benchmark = True
        print(f"[XTTS-v2] VRAM before load: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")

    # Accept Coqui TOS automatically (needed for XTTS-v2 download)
    os.environ["COQUI_TOS_AGREED"] = "1"

    _model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    _ready = True

    if device == "cuda":
        print(f"[XTTS-v2] VRAM after load: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
    print(f"[XTTS-v2] Model ready on {device}.")


def _resolve_speaker_wav(voice_profile_id: str | None = None) -> str:
    """
    Resolve the speaker WAV file to use for TTS.
    If a voice_profile_id is given, use the cloned voice profile.
    Otherwise, use the default reference WAV.
    """
    if voice_profile_id:
        profile_wav = os.path.join(PROFILES_DIR, voice_profile_id, "reference.wav")
        if os.path.exists(profile_wav):
            print(f"[XTTS-v2] Using cloned voice profile: {voice_profile_id}")
            return profile_wav
        else:
            print(f"[XTTS-v2] Profile '{voice_profile_id}' not found, falling back to default.")

    return REFERENCE_WAV


def generate_voice_from_text(
    text: str,
    output_path: str,
    language: str = "tr",
    voice_profile_id: str | None = None,
) -> None:
    """
    Generate speech from text using XTTS-v2 and save as WAV.

    Args:
        text:              Lyrics / text to synthesize.
        output_path:       Full path where the .wav file will be saved.
        language:          BCP-47 language code, e.g. "tr", "en", "de".
                           Must be one of SUPPORTED_LANGUAGES.
        voice_profile_id:  Optional. If provided, uses the cloned voice profile
                           instead of the default reference voice.
    """
    global _model, _ready

    if not _ready:
        load_model()

    # Normalise language code
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        print(f"[XTTS-v2] Unsupported language '{lang}', falling back to 'en'.")
        lang = "en"

    # Resolve speaker WAV (cloned voice or default)
    speaker_wav = _resolve_speaker_wav(voice_profile_id)

    print(f"[XTTS-v2] Generating voice [{lang}] (profile: {voice_profile_id or 'default'}): {text[:60]}...")

    try:
        # Tuning parameters for a more 'expressive' and less 'robotic' voice
        _model.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=speaker_wav,
            language=lang,
            speed=1.0,           # Standard speed
            split_sentences=True # Better prosody for longer texts
        )
        print(f"[XTTS-v2] Voice saved → {output_path}")
    finally:
        # Clean up VRAM after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
