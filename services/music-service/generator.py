import uuid
import os
import scipy.io.wavfile
import torch
from model_loader import get_model_loader

# In Docker, use the shared volume path; locally fallback to local outputs
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class MusicGenerator:
    def __init__(self):
        self.loader = get_model_loader()
        
    def generate(self, prompt: str, duration: int = 10):
        processor, model = self.loader.load()
        
        # Format the inputs
        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.loader.device) for k, v in inputs.items()}
        
        # Calculate max_new_tokens for the requested duration.
        frame_rate = model.config.audio_encoder.frame_rate
        max_new_tokens = int(frame_rate * duration)
        
        with torch.no_grad():
            audio_values = model.generate(**inputs, max_new_tokens=max_new_tokens)
            
        # audio_values shape: (batch_size, num_channels, sequence_length)
        audio = audio_values[0, 0].cpu().numpy()
        sampling_rate = model.config.audio_encoder.sampling_rate
        
        # Generate filename
        filename = f"{uuid.uuid4().hex}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Save as WAV
        scipy.io.wavfile.write(filepath, rate=sampling_rate, data=audio)
        
        return filename
