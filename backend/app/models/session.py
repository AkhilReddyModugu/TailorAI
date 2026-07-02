# Pydantic models for session, JD, and results — mirrors the MongoDB `sessions` schema.

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

SessionStatus = Literal["processing", "completed", "failed"]


class Experience(BaseModel):
    title: str
    company: str
    duration: str
    bullets: list[str] = Field(default_factory=list)


class Education(BaseModel):
    degree: str
    institution: str
    year: str


class Project(BaseModel):
    name: str
    bullets: list[str] = Field(default_factory=list)


class ResumeParsed(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)


class JDParsed(BaseModel):
    title: str = ""
    company: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    key_responsibilities: list[str] = Field(default_factory=list)
    ats_keywords: list[str] = Field(default_factory=list)


class GapReport(BaseModel):
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    match_percentage: int = 0
    ats_keywords_found: list[str] = Field(default_factory=list)
    ats_keywords_missing: list[str] = Field(default_factory=list)
    agent_strategy: str = ""
    agent_reasoning: str = ""


class RewrittenBullet(BaseModel):
    original: str
    rewritten: str
    reason: str


class SelfEvaluation(BaseModel):
    passed: bool = True
    issues_found: list[str] = Field(default_factory=list)
    re_runs: int = 0


class Session(BaseModel):
    """Shape of a document in the `sessions` collection (excluding `_id`)."""

    created_at: datetime
    status: SessionStatus = "processing"
    current_step: int = 0
    current_step_name: str = ""
    error_message: Optional[str] = None

    resume_text: str
    resume_parsed: Optional[ResumeParsed] = None

    jd_raw: str
    jd_parsed: Optional[JDParsed] = None

    gap_report: Optional[GapReport] = None
    rewritten_bullets: list[RewrittenBullet] = Field(default_factory=list)
    cover_letter: Optional[str] = None
    self_evaluation: Optional[SelfEvaluation] = None
