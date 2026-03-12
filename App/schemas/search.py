from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    specialty: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)
    document_ids: list[UUID] = Field(default_factory=list)


class SearchResultItem(BaseModel):
    chunk_id: UUID
    document_id: UUID
    title: str
    content: str
    page_number: int | None = None
    section_title: str | None = None
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total_results: int