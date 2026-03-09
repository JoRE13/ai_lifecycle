from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProblemCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ProblemCreateResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class AttemptResponse(BaseModel):
    id: UUID
    problem_id: UUID
    user_id: UUID
    mode: str
    solution_image_url: str | None
    verdict: str | None
    response_type: str | None
    message_is: str | None
    error_type: str | None = None
    model_name: str | None = None
    prompt_version: str | None = None
    latency_ms: int | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    tokens_thoughts: int | None = None
    tokens_total: int | None = None
    created_at: datetime


class AttemptFeedbackCreateRequest(BaseModel):
    rating: str | None = Field(default=None, max_length=16)
    comment: str | None = None


class AttemptFeedbackResponse(BaseModel):
    id: UUID
    attempt_id: UUID
    user_id: UUID
    rating: str | None
    comment: str | None
    created_at: datetime


class AnalyticsEventResponse(BaseModel):
    id: UUID
    user_id: UUID
    problem_id: UUID | None = None
    attempt_id: UUID | None = None
    event_type: str | None
    mode: str | None
    verdict: str | None
    created_at: datetime
    metadata_json: str | None
