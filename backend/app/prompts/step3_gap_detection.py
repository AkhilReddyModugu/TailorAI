# Step 3: Skill gap detection + adaptive rewrite strategy selection.

from app.models.session import GapReport, JDParsed, ResumeParsed
from app.services.llm_client import call_llm_json

_SCHEMA = """{
  "matching_skills": [string, ...],
  "missing_skills": [string, ...],
  "match_percentage": integer (0-100),
  "ats_keywords_found": [string, ...],
  "ats_keywords_missing": [string, ...],
  "domain_mismatch": boolean,
  "domain_mismatch_reason": string
}"""

_PROMPT = """You are an expert technical recruiter comparing a candidate's resume against a job description and return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- matching_skills: skills present in the candidate's background (skills list, experience, or project bullets) that also appear in the job's required or preferred skills (case-insensitive, allow reasonable synonyms).
- missing_skills: job required/preferred skills not present anywhere in the candidate's background, required skills first.
- match_percentage: 0-100 integer estimate of overall fit, weighted mostly on required_skills coverage with some credit for preferred_skills and relevant experience.
- ats_keywords_found / ats_keywords_missing: overlap between the job's ats_keywords and everything present in the candidate's resume.
- domain_mismatch: true ONLY if the candidate's overall background (job titles, skills, experience) is in an entirely different field than the job posting (e.g. a chef resume for a software engineering role) — not simply missing some skills within the same field.
- domain_mismatch_reason: one sentence justifying the domain_mismatch value.
- Do not invent skills or keywords that are not present in the inputs.

Candidate skills: {resume_skills}

Candidate experience:
{resume_experience}

Candidate projects:
{resume_projects}

Job title: {jd_title}
Job required skills: {jd_required_skills}
Job preferred skills: {jd_preferred_skills}
Job ATS keywords: {jd_ats_keywords}
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


def _choose_strategy(match_percentage: int, domain_mismatch: bool, domain_mismatch_reason: str) -> tuple[str, str]:
    """Adaptive rewrite strategy: how aggressively step 4 should rewrite bullets.

    Domain mismatch overrides the match percentage entirely, since no amount
    of bullet rewriting fixes a candidate applying outside their field.
    """
    if domain_mismatch:
        reason = domain_mismatch_reason or "The candidate's background is in a different field than this role."
        return "skip_mismatch", f"{reason} Skipping rewrite — recommend the candidate reconsider whether this role is a fit."

    if match_percentage > 85:
        return "light_tweaks", f"Match is {match_percentage}%, already strong — applying light keyword tweaks only."

    if match_percentage >= 40:
        return "targeted_rewrite", f"Match is {match_percentage}% — rewriting the weakest bullets to close the gap."

    return "aggressive_rewrite", (
        f"Match is only {match_percentage}% — this is a stretch role; performing a full rewrite "
        "and flagging it as a stretch role."
    )


async def detect_gaps(resume: ResumeParsed, jd: JDParsed) -> GapReport:
    """Compare parsed resume and JD, then pick a rewrite strategy for step 4.

    Agentic decision point: match_percentage (and an explicit domain_mismatch
    signal from the model) drive which rewrite aggressiveness step 4 should
    use, from light keyword tweaks up to a full stretch-role rewrite, or
    skipping the rewrite entirely when the domains don't match.
    """
    prompt = _PROMPT.format(
        schema=_SCHEMA,
        resume_skills=", ".join(resume.skills) or "(none)",
        resume_experience=_format_experience(resume),
        resume_projects=_format_projects(resume),
        jd_title=jd.title or "(unspecified)",
        jd_required_skills=", ".join(jd.required_skills) or "(none)",
        jd_preferred_skills=", ".join(jd.preferred_skills) or "(none)",
        jd_ats_keywords=", ".join(jd.ats_keywords) or "(none)",
    )
    data = await call_llm_json(prompt)

    domain_mismatch = bool(data.pop("domain_mismatch", False))
    domain_mismatch_reason = data.pop("domain_mismatch_reason", "")

    report = GapReport(**data)
    report.agent_strategy, report.agent_reasoning = _choose_strategy(
        report.match_percentage, domain_mismatch, domain_mismatch_reason
    )
    return report
