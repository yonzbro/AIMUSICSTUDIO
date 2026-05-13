import os
import subprocess
import torch
import gc

_ready = False

def is_model_loaded() -> bool:
    return _ready

def load_model():
    global _ready
    _ready = True
    print("Remix service ready (Demucs htdemucs model will download on first request).")

def split_audio(audio_path: str, output_dir: str):
    """Split audio into stems using Demucs htdemucs model via CLI."""
    global _ready
    if not _ready:
        load_model()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Splitting audio on {device}: {audio_path}")

    # Use demucs CLI - most reliable across all versions
    cmd = [
        "python", "-m", "demucs.separate",
        "--two-stems=vocals",
        "-n", "htdemucs",
        "--device", device,
        "-o", output_dir,
        audio_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"Demucs stderr: {result.stderr}")
            raise RuntimeError(f"Demucs failed: {result.stderr}")

        # Demucs outputs to: output_dir/htdemucs/<filename>/vocals.wav, no_vocals.wav
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        stems_dir = os.path.join(output_dir, "htdemucs", base_name)

        stems = []
        if os.path.isdir(stems_dir):
            for f in os.listdir(stems_dir):
                if f.endswith(".wav"):
                    # Move stems to output_dir root for easy serving
                    src = os.path.join(stems_dir, f)
                    dst_name = f"{base_name}_{f}"
                    dst = os.path.join(output_dir, dst_name)
                    os.rename(src, dst)
                    stems.append(dst_name)
                    print(f"Saved stem: {dst_name}")

        return stems

    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
