import subprocess
import os
from gtts import gTTS

def load_model():
    """gTTS requires no model loading - it calls Google TTS API."""
    print("Voice service ready (using gTTS + ffmpeg for WAV conversion).")

def generate_voice_from_text(text: str, output_path: str):
    """Generate speech from text and save as WAV."""
    print(f"Generating voice for: {text[:60]}...")

    # gTTS produces MP3, we convert to WAV with ffmpeg
    mp3_path = output_path.replace(".wav", ".mp3")

    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(mp3_path)

    # Convert MP3 → WAV (mono, 22050 Hz) via ffmpeg
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-ar", "22050",
            "-ac", "1",
            output_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    os.remove(mp3_path)
    print(f"Voice saved to {output_path}")
