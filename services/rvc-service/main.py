from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
from inference import rvc_infer

app = FastAPI(title="RVC Voice Conversion API")

# Paths from environment variables or defaults
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
PROFILES_DIR = os.getenv("PROFILES_DIR", "/app/voice_profiles")

class RVCRequest(BaseModel):
    source_audio_path: str
    voice_profile_id: str
    f0_method: str = "rmvpe"  # rmvpe is best for quality/speed
    f0_up_key: int = 0        # pitch shift
    index_rate: float = 0.75  # strength of cloning

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/model-status")
async def model_status():
    """Returns RVC service status and capabilities."""
    return {
        "loaded": True, # RVC loads models per request in current implementation
        "model_name": "RVC v3 (RMVPE)",
        "description": "High-fidelity voice conversion using Retrieval-based Voice Conversion",
        "gpu_available": True
    }

@app.post("/load-model")
async def trigger_load():
    """Dummy endpoint to satisfy gateway interface; RVC loads models on-demand."""
    return {"status": "ready", "model_name": "RVC v3"}

@app.post("/convert")
async def convert_voice(request: RVCRequest):
    """
    Convert a source audio (usually TTS) into a target voice profile using RVC.
    """
    # 1. Validate source audio
    if not os.path.exists(request.source_audio_path):
        # Try relative to outputs dir
        alt_path = os.path.join(OUTPUT_DIR, os.path.basename(request.source_audio_path))
        if os.path.exists(alt_path):
            request.source_audio_path = alt_path
        else:
            raise HTTPException(status_code=404, detail=f"Source audio not found: {request.source_audio_path}")

    # 2. Resolve voice profile (.pth and .index files)
    profile_path = os.path.join(PROFILES_DIR, request.voice_profile_id)
    pth_file = os.path.join(profile_path, f"{request.voice_profile_id}.pth")
    index_file = os.path.join(profile_path, f"{request.voice_profile_id}.index")

    if not os.path.exists(pth_file):
        raise HTTPException(status_code=404, detail=f"Voice profile model (.pth) not found for: {request.voice_profile_id}")

    # 3. Output path
    output_filename = f"rvc_{os.path.basename(request.source_audio_path)}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # 4. Perform Inference
    try:
        print(f"[RVC] Converting {request.source_audio_path} using {request.voice_profile_id}...")
        
        # We run this in a threadpool because RVC inference is CPU/GPU intensive and blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            rvc_infer, 
            pth_file, 
            index_file, 
            request.source_audio_path, 
            output_path, 
            request.f0_up_key, 
            request.f0_method,
            request.index_rate
        )
        
        return {
            "status": "success",
            "converted_file": output_filename,
            "output_path": output_path
        }
    except Exception as e:
        print(f"[RVC] Error during conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
