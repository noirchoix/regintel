from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str


class Pagination(BaseModel):
    total: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1)
    offset: int = Field(default=0, ge=0)
