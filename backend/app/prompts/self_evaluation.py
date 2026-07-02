# Self-evaluation: check step 4/5 outputs for hallucinations, run after step 5.

from app.models.session import JDParsed, ResumeParsed, RewrittenBullet, SelfEvaluation
from app.services.llm_client import call_llm_json

_SCHEMA = """{
  "passed": boolean,
  "issues_found": [string, ...]
}"""

_PROMPT = """You are a meticulous fact-checker reviewing AI-generated resume/cover-letter output for hallucinations before it reaches the candidate. Return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- issues_found may only contain these exact tags (include a tag if and only if that problem is present):
  - "cover_letter_hallucination": the cover letter claims a skill, tool, or experience not present in the candidate's skills, experience, or projects below.
  - "bullet_fabrication": a rewritten bullet includes a specific number/metric that is not present in its original bullet and not clearly implied by the candidate's other listed skills/experience.
  - "wrong_company_or_title": the cover letter names the wrong company or role title compared to the job title/company below.
- passed is true only if issues_found is empty.
- Be conservative: only flag a clear, concrete mismatch, not stylistic differences.

Candidate skills: {candidate_skills}
Candidate experience:
{candidate_experience}
Candidate projects:
{candidate_projects}

Job title: {jd_title}
Company: {jd_company}

Rewritten bullets (original -> rewritten):
{bullets}

Cover letter:
\"\"\"
{cover_letter}
\"\"\"
"""


def _format_experience(resume: ResumeParsed) -> str:
    lines = []
    for exp in resume.experience:
        bullets = "; ".join(exp.bullets)
        lines.append(f"- {exp.title} at {exp.company} ({exp.duration}): {bullets}")
    return "\n".join(lines) if lines else "(none)"


def _format_projects(resume: ResumeParsed) -> str:
    lines = []
    for proj in resume.projects:
        bullets = "; ".join(proj.bullets)
        lines.append(f"- {proj.name}: {bullets}")
    return "\n".join(lines) if lines else "(none)"


def _format_bullet_pairs(rewritten_bullets: list[RewrittenBullet]) -> str:
    if not rewritten_bullets:
        return "(none)"
    return "\n".join(f'- "{rb.original}" -> "{rb.rewritten}"' for rb in rewritten_bullets)


async def self_evaluate(
    resume: ResumeParsed,
    jd: JDParsed,
    rewritten_bullets: list[RewrittenBullet],
    cover_letter: str | None,
) -> SelfEvaluation:
    """Check step 4/5 outputs for hallucinations against the source resume and JD.

    Agentic decision point: flags cover-letter claims not grounded in the
    resume, fabricated metrics in rewritten bullets, and wrong company/title
    references, so ai_chain.py can decide whether to re-run steps 4/5.
    """
    if cover_letter is None and not rewritten_bullets:
        return SelfEvaluation(passed=True, issues_found=[], re_runs=0)

    prompt = _PROMPT.format(
        schema=_SCHEMA,
        candidate_skills=", ".join(resume.skills) or "(none)",
        candidate_experience=_format_experience(resume),
        candidate_projects=_format_projects(resume),
        jd_title=jd.title or "(unspecified)",
        jd_company=jd.company or "(unspecified)",
        bullets=_format_bullet_pairs(rewritten_bullets),
        cover_letter=cover_letter or "(no cover letter generated)",
    )
    data = await call_llm_json(prompt)
    return SelfEvaluation(
        passed=bool(data.get("passed", True)),
        issues_found=data.get("issues_found", []),
        re_runs=0,
    )
