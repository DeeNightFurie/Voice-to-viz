from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from data_processor import processor
from upload_handler import uploader
from visualizer import viz_engine
import os

app = FastAPI(title="Voice Data Viz App", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("visualizations", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations")
app.mount("/processed_data", StaticFiles(directory="processed_data"), name="processed_data")


@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """Voice command: 'upload data'"""
    # 1) Save file
    upload_info = await uploader.handle_upload(file)

    # 2) Auto-load into processor (latest file with same extension)
    upload_dir = "uploads"
    ext = os.path.splitext(upload_info.filename)[1]
    latest_path = None

    for path in os.listdir(upload_dir):
        if path.endswith(ext):
            full_path = os.path.join(upload_dir, path)
            if latest_path is None or os.path.getmtime(full_path) > os.path.getmtime(latest_path):
                latest_path = full_path

    loaded = False
    if latest_path:
        loaded = processor.load_data(latest_path)
        if loaded:
            processor.save_processed()

    return {
        "message": "Data uploaded successfully",
        "file": upload_info.__dict__,
        "auto_loaded": loaded,
    }


@app.get("/data/status")
def get_data_status():
    """Voice command: 'status' / 'check data'"""
    return processor.get_status()


@app.post("/clean/remove-duplicates")
def remove_duplicates():
    """Voice command: 'remove duplicates'"""
    result = processor.clean_duplicates()
    if result.get("success"):
        processor.save_processed()
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
