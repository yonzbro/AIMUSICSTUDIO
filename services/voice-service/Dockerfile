FROM python:3.10-slim

WORKDIR /app

# ── System dependencies ─────────────────────────────────────────────
# ffmpeg: audio processing
# espeak-ng: reference voice generation at build time + XTTS phonemizer backend
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak-ng \
    libespeak-ng-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ─────────────────────────────────────────────
# Install PyTorch FIRST (CUDA 11.8), then coqui-tts so it can detect torch
COPY requirements.txt .
RUN pip install --default-timeout=3000 --no-cache-dir \
        torch==2.1.2 \
        torchaudio==2.1.2 \
        --index-url https://download.pytorch.org/whl/cu118 \
    && pip install --default-timeout=3000 --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu118

COPY . .

# ── Reference voice (built once, used for every synthesis call) ─────
# espeak-ng produces a sample voice; ffmpeg converts it to XTTS-v2 format
# (22 050 Hz, mono, 16-bit PCM WAV, ≥6 seconds)
RUN espeak-ng \
        -v en \
        -s 130 \
        -w /tmp/ref_raw.wav \
        "Hello, this is the reference voice sample for the AI Music Studio. The system will use this voice to synthesize lyrics into natural expressive speech." \
    && ffmpeg -y \
        -i /tmp/ref_raw.wav \
        -ar 22050 \
        -ac 1 \
        -acodec pcm_s16le \
        /app/reference.wav \
    && rm /tmp/ref_raw.wav

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
