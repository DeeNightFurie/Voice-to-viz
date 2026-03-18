from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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


@app.get("/data/preview")
def data_preview(rows: int = 5):
    """Preview current (cleaned) data"""
    if processor.data is None:
        return {"success": False, "message": "No data loaded", "rows": []}
    return {
        "success": True,
        "rows": processor.get_preview(rows),
        "columns": list(processor.data.columns),
    }

@app.post("/visualize/all")
async def visualize_all():
    print("🔍 DEBUG: visualize_all START")
    status = processor.get_status()
    print(f"🔍 DEBUG: status = {status}")
    
    if not status["loaded"]:
        return {"success": False, "message": "No data loaded"}

    processor.save_processed()
    print(f"🔍 DEBUG: processed_file = '{getattr(processor, 'processed_file', 'MISSING')}'")
    print(f"🔍 DEBUG: visualizations/ exists? {os.path.exists('visualizations/')}")
    
    chart_types = ["bar", "line", "pie", "scatter", "histogram"]
    charts = {}

    for chart_type in chart_types:
        print(f"\n🔍 DEBUG: Creating {chart_type}...")
        result = viz_engine.create_chart(chart_type, {
            "x_column": status["columns"][0] if status["columns"] else None,
            "y_column": status["columns"][1] if len(status["columns"]) > 1 else None,
            "title": f"{chart_type.title()} Chart"
        })
        print(f"🔍 DEBUG: {chart_type} RESULT = {result}")
        if result["success"]:
            charts[chart_type] = result["chart_url"]
        else:
            print(f"🔍 DEBUG: {chart_type} FAILED: {result.get('error', 'No error msg')}")

    print(f"🔍 DEBUG: FINAL charts = {charts}")
    return {"success": True, "charts": charts}


@app.get("/data/download")
def download_cleaned_data():
    """Download cleaned data as CSV (not chart)"""
    if processor.data is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "No data loaded"},
        )


    # Save to a temp CSV
    filename = processor.filename or "cleaned_data"
    csv_path = os.path.join("processed_data", f"{filename}_cleaned.csv")
    processor.data.to_csv(csv_path, index=False)

    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename=f"{filename}_cleaned.csv",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
