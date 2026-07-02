# Request/response schemas for the API layer.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.session import (
    GapReport,
    JDParsed,
    ResumeParsed,
    RewrittenBullet,
    SelfEvaluation,
    SessionStatus,
)


class UploadResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str


class SessionResponse(BaseModel):
    """Full session document returned by GET /api/session/{id}, with `_id` as `id`."""

    id: str
    created_at: datetime
    status: SessionStatus
    current_step: int
    current_step_name: str
    error_message: Optional[str] = None

    resume_text: str
    resume_parsed: Optional[ResumeParsed] = None

    jd_raw: str
    jd_parsed: Optional[JDParsed] = None

    gap_report: Optional[GapReport] = None
    rewritten_bullets: list[RewrittenBullet] = Field(default_factory=list)
    cover_letter: Optional[str] = None
    self_evaluation: Optional[SelfEvaluation] = None
