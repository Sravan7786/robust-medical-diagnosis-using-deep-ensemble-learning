from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import io
import os
from contextlib import asynccontextmanager
from ensemble_model import predict_image, get_models
from datetime import datetime
import time

import threading

from database import init_db, save_diagnosis, get_history

# Set OMP environment variable
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

def log_status(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def background_initialization():
    log_status("Background Task: Pre-warming ensemble models...")
    try:
        init_db() # Initialize DB
        get_models()
        log_status("Background Task: Models loaded and DB initialized.")
    except Exception as e:
        log_status(f"Background Task Error: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start pre-warming in the background so the server starts immediately
    init_thread = threading.Thread(target=background_initialization, daemon=True)
    init_thread.start()
    yield

app = FastAPI(lifespan=lifespan)

# Optimization: Add GZip compression for faster data transfer
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/health")
async def health_check():
    """Rapid health check for frontend heartbeat."""
    return {
        "status": "online",
        "engine": "Robust Deep Ensemble",
        "server_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "version": "2.1.0"
    }

@app.get("/history")
async def history():
    return get_history()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        image_bytes = io.BytesIO(contents)
        result = predict_image(image_bytes)
        
        # Save to database
        save_diagnosis(
            modality=result['modality'],
            condition=result['condition'],
            confidence=result['confidence'],
            report=result['report'],
            filename=file.filename
        )
        
        return result
    except Exception as e:
        log_status(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Optimized for Windows: single worker for ML models, 0.0.0.0 for network transparency
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5055, 
        reload=False, 
        workers=1,
        log_level="info"
    )
