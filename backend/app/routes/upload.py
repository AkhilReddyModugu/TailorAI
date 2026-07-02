# POST /api/upload

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from app.database import get_db
from app.models.schemas import UploadResponse
from app.services.ai_chain import run_chain
from app.services.pdf_parser import PDFParseError, extract_text_from_pdf

router = APIRouter()


@router.post("/api/upload", response_model=UploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    job_description: str = Form(...),
) -> UploadResponse:
    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    pdf_bytes = await resume.read()

    try:
        resume_text = extract_text_from_pdf(pdf_bytes)
    except PDFParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session_doc = {
        "created_at": datetime.now(timezone.utc),
        "status": "processing",
        "current_step": 0,
        "current_step_name": "Queued",
        "error_message": None,
        "resume_text": resume_text,
        "resume_parsed": None,
        "jd_raw": job_description,
        "jd_parsed": None,
        "gap_report": None,
        "rewritten_bullets": [],
        "cover_letter": None,
        "self_evaluation": None,
    }

    db = get_db()
    result = await db.sessions.insert_one(session_doc)
    session_id = str(result.inserted_id)

    background_tasks.add_task(run_chain, session_id, resume_text, job_description)

    return UploadResponse(
        session_id=session_id,
        status="processing",
        message="Analysis started",
    )
