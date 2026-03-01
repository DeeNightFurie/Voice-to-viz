from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from data_processor import processor
from upload_handler import uploader
from visualizer import viz_engine
import os

app = FastAPI(title="Voice Data Viz App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("uploads", exist_ok=True)
os.makedirs("visualizations", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations")
app.mount("/processed_data", StaticFiles(directory="processed_data"), name="processed_data")

@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """Voice command: 'upload data'"""
    upload_info = await uploader.handle_upload(file)
    return {"message": "Data uploaded successfully", "file": upload_info.__dict__}

@app.get("/data/status")
def get_data_status():
    """Voice command: 'check data status'"""
    return processor.get_status()

@app.post("/clean/remove-duplicates")
def remove_duplicates():
    """Voice command: 'remove duplicates'"""
    result = processor.clean_duplicates()
    processor.save_processed()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
