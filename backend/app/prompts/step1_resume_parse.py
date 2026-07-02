# Step 1: Resume parsing prompt with self-healing retry.

from app.models.session import ResumeParsed
from app.services.llm_client import call_llm_json

_SCHEMA = """{
  "name": string,
  "email": string,
  "phone": string,
  "skills": [string, ...],
  "experience": [
    {"title": string, "company": string, "duration": string, "bullets": [string, ...]}
  ],
  "education": [
    {"degree": string, "institution": string, "year": string}
  ],
  "projects": [
    {"name": string, "bullets": [string, ...]}
  ]
}"""

_BASE_PROMPT = """You are an expert resume parser. Extract structured data from the resume text below and return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- Use "" for any missing string field, [] for any missing list.
- Every accomplishment/description under an experience or project entry must become its own bullet string.
- Do not invent information that is not present in the resume text.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""

_AGGRESSIVE_PROMPT = """You are an expert resume parser doing a SECOND, more thorough pass because the first pass under-extracted this resume. Be aggressive:
- Infer skills from anything mentioned anywhere in the text (job titles, tool/library names inside project or experience descriptions, technologies implied by the work described), not just an explicit "Skills" section.
- Split every distinct accomplishment or responsibility, even short ones, into its own bullet string instead of merging them.

Return ONLY valid JSON (no markdown, no commentary) matching exactly this schema:

{schema}

Rules:
- Use "" for any missing string field, [] for any missing list.
- Do not invent information that is not present in the resume text.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""


def _total_bullets(parsed: ResumeParsed) -> int:
    experience_bullets = sum(len(exp.bullets) for exp in parsed.experience)
    project_bullets = sum(len(proj.bullets) for proj in parsed.projects)
    return experience_bullets + project_bullets


async def parse_resume(resume_text: str) -> ResumeParsed:
    """Parse resume text into structured data, self-healing if the first pass is too sparse.

    Agentic decision point: if the parsed result has no skills or fewer than
    3 total bullets across experience/projects, the first pass likely
    under-extracted the resume, so we retry once with a more aggressive prompt.
    """
    data = await call_llm_json(_BASE_PROMPT.format(schema=_SCHEMA, resume_text=resume_text))
    parsed = ResumeParsed(**data)

    if not parsed.skills or _total_bullets(parsed) < 3:
        data = await call_llm_json(_AGGRESSIVE_PROMPT.format(schema=_SCHEMA, resume_text=resume_text))
        parsed = ResumeParsed(**data)

    return parsed
