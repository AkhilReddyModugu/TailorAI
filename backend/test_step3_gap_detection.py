"""Manual test script for app.prompts.step3_gap_detection.

Uses the outputs of steps 1 and 2 as input, so it also exercises the full
parse -> analyze -> gap-detect chain.

Run with: python test_step3_gap_detection.py
"""

import asyncio
import json

from app.prompts.step1_resume_parse import parse_resume
from app.prompts.step2_jd_analysis import analyze_jd
from app.prompts.step3_gap_detection import detect_gaps

SAMPLE_RESUME = (
    "Akhil Kumar, Software Engineer. Skills: Python, React, Flask, AWS. "
    "Experience: Software Dev at XYZ Corp (2022-2024) - Built REST APIs using Flask, "
    "Deployed services on AWS. Projects: ChatBot - Built using OpenAI API."
)

SAMPLE_JD = (
    "Senior Backend Engineer at Acme Inc. Must have: Go, Kubernetes, PostgreSQL. "
    "Nice to have: Python, AWS. You will design distributed systems and implement "
    "CI/CD pipelines for scalable microservices."
)


async def main() -> None:
    resume = await parse_resume(SAMPLE_RESUME)
    jd = await analyze_jd(SAMPLE_JD)
    gap_report = await detect_gaps(resume, jd)

    print("=== Resume Parsed ===")
    print(json.dumps(resume.model_dump(), indent=2))
    print("\n=== JD Parsed ===")
    print(json.dumps(jd.model_dump(), indent=2))
    print("\n=== Gap Report ===")
    print(json.dumps(gap_report.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
