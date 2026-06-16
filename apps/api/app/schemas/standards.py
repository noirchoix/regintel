from datetime import datetime

from pydantic import BaseModel, Field


class StandardDocumentRead(BaseModel):
    id: str
    title: str
    framework: str
    jurisdiction: str
    version: str
    status: str
    source_filename: str
    chunk_count: int
    created_at: datetime


class IngestionJobRead(BaseModel):
    id: str
    document_id: str
    status: str
    error_message: str | None = None
    enqueued_at: datetime
    completed_at: datetime | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=3)
    jurisdiction: str | None = None
    frameworks: list[str] = Field(default_factory=list)
    limit: int = Field(default=8, ge=1, le=20)
