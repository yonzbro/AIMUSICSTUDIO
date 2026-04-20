import torch
import os

_loaded = False

def load_model():
    """Clone service stub — real implementation requires OpenVoice checkpoints."""
    global _loaded
    _loaded = True
    print("Clone service ready (demonstration mode).")
    print("NOTE: Real voice cloning requires OpenVoice checkpoint files.")

def extract_voice_embedding(audio_path: str, profile_id: str):
    """
    Stub implementation: saves a placeholder embedding tensor.
    Real implementation would use OpenVoice se_extractor.get_se().
    """
    print(f"Processing voice sample: {audio_path}")

    output_dir = os.path.dirname(audio_path)
    profile_path = os.path.join(output_dir, f"{profile_id}_se.pth")

    # Save a dummy 256-dim embedding as placeholder
    dummy_embedding = torch.zeros(256)
    torch.save(dummy_embedding, profile_path)

    print(f"Voice profile stub saved: {profile_path}")
