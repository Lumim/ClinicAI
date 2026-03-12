from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


FeedbackRating = Literal["helpful", "unsafe", "incomplete"]


class FeedbackCreate(BaseModel):
    query_log_id: UUID
    rating: FeedbackRating
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: UUID
    query_log_id: UUID
    rating: FeedbackRating
    comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)