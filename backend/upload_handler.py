'''Purpose: Secure file upload with size limits (10MB), type validation (CSV/Excel only), unique filenames to prevent overwrites, and automatic cleanup.

Security Features:
MIME type validation
Size limits
UUID filenames (no path traversal)
Temporary storage with cleanup'''

import os
import uuid
from pathlib import Path
from fastapi import UploadFile, File, HTTPException
from typing import List
import mimetypes
import pandas as pd 
from models import FileUpload

class UploadHandler:
    def __init__(self):
        self.upload_dir = "uploads/"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def handle_upload(self, file: UploadFile = File(...)) -> FileUpload:
        """Secure file upload with validation"""
        # Validate content type
        content_type = file.content_type or ''
        if content_type not in self.allowed_types:
            raise HTTPException(400, "Only CSV and Excel files allowed")
        
        # Validate size
        file_size = 0
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > self.max_file_size:
            raise HTTPException(400, "File too large (max 10MB)")
        
        # Generate secure filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        filepath = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        with open(filepath, "wb") as buffer:
            buffer.write(contents)
        
        return FileUpload(
            filename=file.filename,
            size=file_size,
            content_type=content_type,
            uploaded_at=pd.Timestamp.now()
        )
    
    def get_uploaded_files(self) -> List[str]:
        """List all uploaded files"""
        files = []
        for file in Path(self.upload_dir).glob("*.csv"):
            files.append(file.name)
        for file in Path(self.upload_dir).glob("*.xlsx"):
            files.append(file.name)
        return files
    
    def cleanup_old_files(self, hours: int = 24):
        """Cleanup old uploads (security)"""
        cutoff = pd.Timestamp.now() - pd.Timedelta(hours=hours)
        for file_path in Path(self.upload_dir).glob("*"):
            if file_path.stat().st_mtime < cutoff.timestamp():
                file_path.unlink()

# Global upload handler
uploader = UploadHandler()
