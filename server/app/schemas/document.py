from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_size: int
    page_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    uploaded: List[DocumentResponse]
    duplicates: List[str] = []
    message: str
