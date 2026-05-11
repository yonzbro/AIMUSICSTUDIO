# 🔊 Sıcumaı AI Music Studio

**Sıcumaı** is a professional-grade, multi-stage AI music generation studio. It allows users to generate full songs (lyrics + music + voice), remix existing audio into stems, and create high-fidelity digital twins of any voice via cloning.

![Sıcumaı Dashboard](https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&q=80&w=1000)

## 🚀 Features

- **Multi-Stage AI Pipeline**: One prompt to generate everything.
  - **Lyrics**: Powered by Qwen2-1.5B (finetuned for songwriting).
  - **Music**: Powered by Facebook MusicGen (Small/Medium).
  - **Voice Synthesis**: Expressive TTS via Coqui XTTS-v2.
- **High-Fidelity RVC**: Integration of Retrieval-based Voice Conversion for maximum vocal realism.
- **Stem Separation (Remix)**: De-mix any song into Vocals, Drums, Bass, and Other tracks using Demucs.
- **Voice Cloning**: Create a permanent digital profile from just 30 seconds of audio.
- **GPU Accelerated**: Optimized for NVIDIA RTX GPUs (CUDA support).

## 🛠️ Tech Stack

- **Frontend**: Flutter (Windows/Android/iOS support).
- **Gateway**: FastAPI + HTTPX (Async Orchestrator).
- **Microservices**:
  - `lyrics-service`: Python + Transformers (Qwen2).
  - `music-service`: Python + Audiocraft.
  - `voice-service`: Python + Coqui TTS.
  - `remix-service`: Python + Demucs.
  - `clone-service`: Python + Soundfile/Librosa.
  - `rvc-service`: Python + RVC-v3 (RMVPE).

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU with CUDA drivers installed
- NVIDIA Container Toolkit

### Quick Start
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yonzbro/AIMUSICSTUDIO.git
   cd AIMUSICSTUDIO
   ```

2. **Launch Microservices**:
   ```bash
   docker-compose up -d
   ```

3. **Run the Flutter App**:
   ```bash
   cd mobile-app
   flutter run -d windows
   ```

## 🎹 Usage

1. **Warmup**: Open the app and click **"Warmup All"** on the home screen to pre-load AI models into VRAM.
2. **Clone**: Go to **Voice Clone**, upload a clean sample of your voice.
3. **Create**: Go to **Create Song**, select your cloned voice profile, enable **RVC**, and describe your song.
4. **Remix**: Upload any song to the **Remix** section to get separated instrumental tracks.

## 📄 License
This project is for educational and creative purposes. Models used are subject to their respective licenses (CC-BY-NC, MIT, etc.).

---
*Created by Antigravity Team for Sıcumaı Project.*
