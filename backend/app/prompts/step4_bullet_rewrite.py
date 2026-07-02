# Step 4: Strategy-aware bullet rewrite, driven by step 3's agent_strategy.

from app.models.session import GapReport, JDParsed, ResumeParsed, RewrittenBullet
from app.services.llm_client import call_llm_json

_SCHEMA = """{
  "rewritten_bullets": [
    {"original": string, "rewritten": string, "reason": string}
  ]
}"""

_BASE_INSTRUCTIONS = """You are an expert resume writer. Return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- "original" must be copied exactly, verbatim, from one of the candidate's bullets listed below.
- "reason" is one sentence explaining what changed and why.
- Do not invent metrics, tools, or accomplishments that aren't grounded in the original bullet or the candidate's listed skills.
- Every bullet you touch must appear in the output; do not include bullets you didn't change.

{strategy_instructions}

Job title: {jd_title}
Job required skills: {jd_required_skills}
Job preferred skills: {jd_preferred_skills}
Missing ATS keywords to work in where truthful: {ats_keywords_missing}

Candidate's current bullets:
{bullets}
"""

_STRATEGY_INSTRUCTIONS = {
    "light_tweaks": (
        "Strategy: LIGHT TWEAKS. The candidate is already a strong match. Only adjust wording on bullets "
        "to naturally include the missing ATS keywords listed below where truthful. Do not restructure "
        "sentences, do not add metrics, and do not touch bullets that don't need a keyword tweak."
    ),
    "targeted_rewrite": (
        "Strategy: TARGETED REWRITE. Identify the 3-5 weakest bullets (vaguest, least quantified, or least "
        "relevant to the job) and rewrite only those. Add plausible quantifiable metrics grounded in the "
        "original bullet, incorporate missing ATS keywords naturally, and strengthen action verbs."
    ),
    "aggressive_rewrite": (
        "Strategy: AGGRESSIVE REWRITE. This is a stretch role for the candidate (match is below 40%). "
        "Rewrite ALL of the candidate's bullets. Add plausible quantifiable metrics, incorporate missing "
        "ATS keywords naturally, and strengthen action verbs throughout, while staying grounded in what "
        "the candidate actually did."
    ),
}


def _collect_bullets(resume: ResumeParsed) -> list[str]:
    bullets: list[str] = []
    for exp in resume.experience:
        bullets.extend(exp.bullets)
    for proj in resume.projects:
        bullets.extend(proj.bullets)
    return bullets


def _format_bullets(bullets: list[str]) -> str:
    return "\n".join(f"- {b}" for b in bullets) if bullets else "(none)"


async def rewrite_bullets(
    resume: ResumeParsed, jd: JDParsed, gap_report: GapReport
) -> list[RewrittenBullet]:
    """Rewrite resume bullets using a prompt chosen by step 3's agent_strategy.

    Agentic decision point: the strategy computed in step 3 (light_tweaks,
    targeted_rewrite, aggressive_rewrite, skip_mismatch) selects a different
    prompt here, from touching almost nothing up to rewriting every bullet.
    skip_mismatch skips the Gemini call entirely since rewriting bullets
    can't fix an application to the wrong field.
    """
    strategy = gap_report.agent_strategy

    if strategy == "skip_mismatch":
        return []

    strategy_instructions = _STRATEGY_INSTRUCTIONS.get(strategy)
    if strategy_instructions is None:
        raise ValueError(f"Unknown agent_strategy: {strategy!r}")

    bullets = _collect_bullets(resume)
    prompt = _BASE_INSTRUCTIONS.format(
        schema=_SCHEMA,
        strategy_instructions=strategy_instructions,
        jd_title=jd.title or "(unspecified)",
        jd_required_skills=", ".join(jd.required_skills) or "(none)",
        jd_preferred_skills=", ".join(jd.preferred_skills) or "(none)",
        ats_keywords_missing=", ".join(gap_report.ats_keywords_missing) or "(none)",
        bullets=_format_bullets(bullets),
    )
    data = await call_llm_json(prompt)
    return [RewrittenBullet(**item) for item in data.get("rewritten_bullets", [])]
