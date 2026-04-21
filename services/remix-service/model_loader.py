import os
import torch
import gc
from pathlib import Path

_ready = False

def is_model_loaded() -> bool:
    return _ready

def load_model():
    global _ready
    _ready = True
    print("Remix service ready (Demucs htdemucs model will download on first request).")

def split_audio(audio_path: str, output_dir: str):
    """Split audio into stems using Demucs htdemucs model."""
    global _ready
    if not _ready:
        load_model()

    from demucs.api import Separator
    from demucs.audio import save_audio

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Splitting audio on {device}: {audio_path}")

    # Instantiate locally so memory is freed after each request
    separator = Separator("htdemucs", device=device)

    try:
        origin, separated = separator.separate_audio_file(Path(audio_path))

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        stems = []

        for stem_name, audio_tensor in separated.items():
            out_file = f"{stem_name}_{base_name}.wav"
            out_path = os.path.join(output_dir, out_file)
            save_audio(audio_tensor, out_path, samplerate=separator.samplerate)
            stems.append(out_file)
            print(f"Saved stem: {out_file}")

        return stems

    finally:
        del separator
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
