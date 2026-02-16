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
    solution_image_key: str | None
    verdict: str | None
    response_type: str | None
    message_is: str | None
    created_at: datetime
