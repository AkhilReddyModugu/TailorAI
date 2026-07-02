# Step 5: Strategy-aware cover letter generation, driven by step 3's agent_strategy.

from app.models.session import GapReport, JDParsed, ResumeParsed, RewrittenBullet
from app.services.llm_client import call_llm_json

_SCHEMA = """{
  "cover_letter": string
}"""

_BASE_INSTRUCTIONS = """You are an expert cover letter writer. Return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- "cover_letter" is a complete, ready-to-send cover letter (3-4 paragraphs), addressed generically (e.g. "Dear Hiring Manager,") unless a company name is given, in which case reference the company by name.
- Do not invent metrics, tools, employers, or accomplishments that aren't grounded in the candidate's background below.
- Naturally work in the ATS keywords listed below where truthful.
- Sign off with the candidate's name.

{strategy_instructions}

Candidate name: {candidate_name}
Candidate skills: {candidate_skills}
Candidate achievements:
{candidate_bullets}

Job title: {jd_title}
Company: {jd_company}
Matching skills: {matching_skills}
Missing skills: {missing_skills}
ATS keywords to work in where truthful: {ats_keywords_missing}
"""

_STRATEGY_INSTRUCTIONS = {
    "light_tweaks": (
        "Strategy: CONFIDENT DIRECT FIT. The candidate is a strong match (over 85%). Write a confident "
        "cover letter that directly connects the candidate's existing experience and skills to the role's "
        "requirements. Do not hedge, and do not mention any skill gaps."
    ),
    "targeted_rewrite": (
        "Strategy: BRIDGE THE GAP. The candidate is a solid but partial match (40-85%). Lead with the "
        "candidate's strongest matching skills and achievements, and frame any missing skills as areas the "
        "candidate is actively developing rather than as weaknesses. Keep the tone confident and forward-looking."
    ),
    "aggressive_rewrite": (
        "Strategy: STRETCH ROLE / GROWTH NARRATIVE. This is a stretch role for the candidate (match below 40%). "
        "Lead with transferable skills and genuine enthusiasm for the field, and build an honest growth "
        "narrative around the gap rather than implying qualifications the candidate doesn't have."
    ),
}


def _collect_bullets(resume: ResumeParsed, rewritten_bullets: list[RewrittenBullet]) -> list[str]:
    if rewritten_bullets:
        return [rb.rewritten for rb in rewritten_bullets]
    bullets: list[str] = []
    for exp in resume.experience:
        bullets.extend(exp.bullets)
    for proj in resume.projects:
        bullets.extend(proj.bullets)
    return bullets


def _format_bullets(bullets: list[str]) -> str:
    return "\n".join(f"- {b}" for b in bullets) if bullets else "(none)"


async def generate_cover_letter(
    resume: ResumeParsed,
    jd: JDParsed,
    gap_report: GapReport,
    rewritten_bullets: list[RewrittenBullet],
) -> str | None:
    """Generate a cover letter using a tone/strategy chosen by step 3's agent_strategy.

    Agentic decision point: reuses the strategy computed in step 3 (light_tweaks,
    targeted_rewrite, aggressive_rewrite, skip_mismatch) to pick the cover
    letter's framing, from a confident direct-fit pitch up to an honest
    stretch-role growth narrative. skip_mismatch skips generation entirely,
    since no cover letter framing fixes an application to the wrong field.
    """
    strategy = gap_report.agent_strategy

    if strategy == "skip_mismatch":
        return None

    strategy_instructions = _STRATEGY_INSTRUCTIONS.get(strategy)
    if strategy_instructions is None:
        raise ValueError(f"Unknown agent_strategy: {strategy!r}")

    prompt = _BASE_INSTRUCTIONS.format(
        schema=_SCHEMA,
        strategy_instructions=strategy_instructions,
        candidate_name=resume.name or "(unspecified)",
        candidate_skills=", ".join(resume.skills) or "(none)",
        candidate_bullets=_format_bullets(_collect_bullets(resume, rewritten_bullets)),
        jd_title=jd.title or "(unspecified)",
        jd_company=jd.company or "(unspecified)",
        matching_skills=", ".join(gap_report.matching_skills) or "(none)",
        missing_skills=", ".join(gap_report.missing_skills) or "(none)",
        ats_keywords_missing=", ".join(gap_report.ats_keywords_missing) or "(none)",
    )
    data = await call_llm_json(prompt)
    return data.get("cover_letter")
