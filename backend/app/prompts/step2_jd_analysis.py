# Step 2: Job description analysis prompt.

from app.models.session import JDParsed
from app.services.llm_client import call_llm_json

_SCHEMA = """{
  "title": string,
  "company": string,
  "required_skills": [string, ...],
  "preferred_skills": [string, ...],
  "key_responsibilities": [string, ...],
  "ats_keywords": [string, ...]
}"""

_PROMPT = """You are an expert technical recruiter. Extract structured data from the job description below and return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- Use "" for any missing string field, [] for any missing list.
- required_skills are skills explicitly stated as must-have/required; preferred_skills are those marked nice-to-have/preferred/bonus.
- key_responsibilities are the core duties described for the role, each as its own string.
- ats_keywords are the specific terms (technologies, tools, certifications, methodologies) an ATS system would scan for, deduplicated.
- Do not invent information that is not present in the job description text.

Job description:
\"\"\"
{jd_text}
\"\"\"
"""


async def analyze_jd(jd_text: str) -> JDParsed:
    """Parse a raw job description into structured data."""
    data = await call_llm_json(_PROMPT.format(schema=_SCHEMA, jd_text=jd_text))
    return JDParsed(**data)
