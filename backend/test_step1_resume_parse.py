"""Manual test script for app.prompts.step1_resume_parse.

Run with: python test_step1_resume_parse.py
"""

import asyncio
import json

from app.prompts.step1_resume_parse import parse_resume

SAMPLE_RESUME = (
    "Akhil Kumar, Software Engineer. Skills: Python, React, Flask, AWS. "
    "Experience: Software Dev at XYZ Corp (2022-2024) - Built REST APIs using Flask, "
    "Deployed services on AWS. Projects: ChatBot - Built using OpenAI API."
)


async def main() -> None:
    parsed = await parse_resume(SAMPLE_RESUME)
    print(json.dumps(parsed.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
