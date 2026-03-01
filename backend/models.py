from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from enum import Enum
import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime.datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class FileUpload(BaseModel):
    filename: str
    size: int
    content_type: str
    uploaded_at: datetime.datetime

class CleaningOperation(BaseModel):
    operation: str  # "remove_duplicates", "fill_missing", "drop_columns"
    column: Optional[str] = None
    value: Optional[Any] = None

class CleaningRequest(BaseModel):
    operations: List[CleaningOperation]

class VizType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"

class VisualizationRequest(BaseModel):
    viz_type: VizType
    x_column: str
    y_column: Optional[str] = None
    group_by: Optional[str] = None
    title: Optional[str] = "Data Visualization"

class DataStatus(BaseModel):
    uploaded: bool
    cleaned: bool
    visualized: bool
    filename: Optional[str] = None
