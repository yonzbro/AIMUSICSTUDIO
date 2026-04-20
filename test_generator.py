import sys
import os

# Add backend directory to path so it can import services
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.services.music_service.generator import MusicGenerator

def run_test():
    prompt = "a fast-paced retro electronic arcade game beat"
    duration = 5 # shorter for faster testing
    print(f"Testing generation for: '{prompt}'")
    
    gen = MusicGenerator()
    filename = gen.generate(prompt=prompt, duration=duration)
    
    print(f"Test complete. Emitted file: {filename}")
    print(f"Location: backend/outputs/{filename}")

if __name__ == "__main__":
    run_test()
