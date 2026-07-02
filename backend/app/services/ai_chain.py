# The 5-step agentic prompt chain, wired as a FastAPI BackgroundTask from POST /api/upload.

from bson import ObjectId

from app.database import get_db
from app.prompts.self_evaluation import self_evaluate
from app.prompts.step1_resume_parse import parse_resume
from app.prompts.step2_jd_analysis import analyze_jd
from app.prompts.step3_gap_detection import detect_gaps
from app.prompts.step4_bullet_rewrite import rewrite_bullets
from app.prompts.step5_cover_letter import generate_cover_letter
from app.services.llm_client import LLMCallError

_STEP_NAMES = {
    1: "Parsing resume...",
    2: "Analyzing job description...",
    3: "Detecting skill gaps...",
    4: "Rewriting resume bullets...",
    5: "Generating cover letter...",
}


async def _update_session(session_id: ObjectId, **fields) -> None:
    db = get_db()
    await db.sessions.update_one({"_id": session_id}, {"$set": fields})


async def _set_step(session_id: ObjectId, step: int) -> None:
    await _update_session(session_id, current_step=step, current_step_name=_STEP_NAMES[step])


async def _fail_session(session_id: ObjectId, message: str) -> None:
    await _update_session(session_id, status="failed", error_message=message)


async def run_chain(session_id: str, resume_text: str, jd_text: str) -> None:
    """Run the full 5-step agentic chain for a session, persisting each step's output.

    Each step's result is saved to MongoDB as soon as it's ready so the
    frontend can poll GET /api/session/{id} for live progress. Any LLM
    failure (after llm_client's internal retry) fails the whole session
    rather than leaving it stuck in "processing".
    """
    oid = ObjectId(session_id)

    try:
        # Step 1: Parse resume (self-healing retry lives inside parse_resume)
        await _set_step(oid, 1)
        resume = await parse_resume(resume_text)
        await _update_session(oid, resume_parsed=resume.model_dump())

        # Step 2: Analyze JD
        await _set_step(oid, 2)
        jd = await analyze_jd(jd_text)
        await _update_session(oid, jd_parsed=jd.model_dump())

        # Step 3: Gap detection + adaptive rewrite-strategy decision
        await _set_step(oid, 3)
        gap_report = await detect_gaps(resume, jd)
        await _update_session(oid, gap_report=gap_report.model_dump())

        # Step 4: Bullet rewrite (strategy-aware; empty for skip_mismatch)
        await _set_step(oid, 4)
        rewritten_bullets = await rewrite_bullets(resume, jd, gap_report)
        await _update_session(oid, rewritten_bullets=[rb.model_dump() for rb in rewritten_bullets])

        # Step 5: Cover letter (strategy-aware; None for skip_mismatch)
        await _set_step(oid, 5)
        cover_letter = await generate_cover_letter(resume, jd, gap_report, rewritten_bullets)
        await _update_session(oid, cover_letter=cover_letter)

        # Agentic self-evaluation: check for hallucinations, re-run the
        # offending step once each if found.
        await _update_session(oid, current_step_name="Reviewing output for accuracy...")
        evaluation = await self_evaluate(resume, jd, rewritten_bullets, cover_letter)

        re_runs = 0
        if not evaluation.passed:
            if "bullet_fabrication" in evaluation.issues_found and rewritten_bullets:
                rewritten_bullets = await rewrite_bullets(resume, jd, gap_report)
                await _update_session(oid, rewritten_bullets=[rb.model_dump() for rb in rewritten_bullets])
                re_runs += 1
            if (
                "cover_letter_hallucination" in evaluation.issues_found
                or "wrong_company_or_title" in evaluation.issues_found
            ) and cover_letter is not None:
                cover_letter = await generate_cover_letter(resume, jd, gap_report, rewritten_bullets)
                await _update_session(oid, cover_letter=cover_letter)
                re_runs += 1
        evaluation.re_runs = re_runs

        await _update_session(oid, self_evaluation=evaluation.model_dump(), status="completed")

    except LLMCallError as exc:
        await _fail_session(oid, f"AI processing failed: {exc}")
    except Exception as exc:  # noqa: BLE001
        await _fail_session(oid, f"Unexpected error while processing: {exc}")
