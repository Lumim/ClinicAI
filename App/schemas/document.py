from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


DocumentStatus = Literal["uploaded", "parsed", "indexed", "failed"]
SourceType = Literal["guideline", "protocol", "formulary", "sop"]


class DocumentBase(BaseModel):
    title: str
    source_name: str
    source_type: SourceType
    specialty: str
    version_label: str
    publication_date: date | None = None


class DocumentCreate(DocumentBase):
    file_path: str


class DocumentResponse(DocumentBase):
    id: UUID
    file_path: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentIndexResponse(BaseModel):
    document_id: UUID
    status: str
    chunks_created: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]