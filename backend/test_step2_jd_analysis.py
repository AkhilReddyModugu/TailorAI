"""Manual test script for app.prompts.step2_jd_analysis.

Run with: python test_step2_jd_analysis.py
"""

import asyncio
import json

from app.prompts.step2_jd_analysis import analyze_jd

SAMPLE_JD = (
    "Senior Backend Engineer at Acme Inc. Must have: Go, Kubernetes, PostgreSQL. "
    "Nice to have: Python, AWS. You will design distributed systems and implement "
    "CI/CD pipelines for scalable microservices."
)


async def main() -> None:
    parsed = await analyze_jd(SAMPLE_JD)
    print(json.dumps(parsed.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
