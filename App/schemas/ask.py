from uuid import UUID

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    specialty: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)
    document_ids: list[UUID] = Field(default_factory=list)


class CitationItem(BaseModel):
    document_id: UUID
    title: str
    page_number: int | None = None
    section_title: str | None = None
    chunk_id: UUID


class AskResponse(BaseModel):
    answer: str
    refused: bool
    citations: list[CitationItem]
    retrieved_chunks: int