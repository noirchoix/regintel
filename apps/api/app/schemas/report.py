from datetime import datetime
from pydantic import BaseModel


class ReportRequest(BaseModel):
    assessment_id: str


class ReportResponse(BaseModel):
    artifact_id: str
    format: str
    storage_url: str | None = None
    created_at: datetime
    status: str = 'completed'
