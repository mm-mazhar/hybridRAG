from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class PublicConfigResponse(BaseModel):
    model: str
    models: list[str]
    embedding_model: str


class DocumentOut(BaseModel):
    id: str
    source_type: str
    source_name: str
    row_count: int
    created_at: str | None = None


class DocumentDeleted(BaseModel):
    status: str = "deleted"
    document_id: str


class DocumentsCleared(BaseModel):
    status: str = "cleared"
    dropped: int


class UrlIngestRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)


class WebsiteIngestRequest(BaseModel):
    base_url: str = Field(min_length=8, max_length=2048)
    sitemap_filename: str = Field(default="sitemap.xml", max_length=256)


class IngestResponse(BaseModel):
    document_id: str
    row_count: int
    source_type: str
    source_name: str


class RetrieveRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=200)
    query: str = Field(min_length=1, max_length=8000)
    limit: int | None = Field(default=None, ge=1, le=20)


class ChunkOut(BaseModel):
    text: str
    filename: str | None
    page_numbers: list[int] | None
    title: str | None
    source: str


class RetrieveResponse(BaseModel):
    chunks: list[ChunkOut]
    hybrid: bool = False
    fts: bool = False
    multi_query: bool = False
    queries: list[str] = Field(default_factory=list)


class MemorySaveRequest(BaseModel):
    document_id: str = Field(min_length=1, max_length=200)
    messages: list[dict[str, Any]]
