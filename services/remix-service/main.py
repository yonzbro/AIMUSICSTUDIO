from fastapi import FastAPI, UploadFile, File
import os
from model_loader import load_model, split_audio

app = FastAPI(title="Remix Service API")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    load_model()

@app.post("/remix")
async def remix(file: UploadFile = File(...)):
    temp_path = os.path.join(OUTPUT_DIR, f"remix_input_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    stems = split_audio(temp_path, OUTPUT_DIR)
    
    return {"stems": stems}
