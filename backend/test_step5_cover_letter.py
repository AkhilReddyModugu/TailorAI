"""Manual test script for app.prompts.step5_cover_letter.

Uses the outputs of steps 1-4 as input, so it also exercises the full
parse -> analyze -> gap-detect -> rewrite -> cover-letter chain. Runs the
same three sample resume/JD pairs as test_step4_bullet_rewrite.py so each
agent_strategy bucket (light_tweaks, targeted_rewrite/aggressive_rewrite,
skip_mismatch) is covered.

Run with: python test_step5_cover_letter.py
"""

import asyncio

from app.prompts.step1_resume_parse import parse_resume
from app.prompts.step2_jd_analysis import analyze_jd
from app.prompts.step3_gap_detection import detect_gaps
from app.prompts.step4_bullet_rewrite import rewrite_bullets
from app.prompts.step5_cover_letter import generate_cover_letter

CASES = {
    "strong match -> light_tweaks": (
        "Akhil Kumar, Senior Backend Engineer. Skills: Python, Go, Kubernetes, PostgreSQL, AWS, "
        "Docker, CI/CD. Experience: Backend Engineer at Acme Inc (2021-2024) - Designed and deployed "
        "microservices using Go and Kubernetes, Built CI/CD pipelines with Docker and Jenkins, "
        "Optimized PostgreSQL queries reducing latency. Projects: Order Service - Built using Go, "
        "Kubernetes, and PostgreSQL.",
        "Senior Backend Engineer at Acme Inc. Must have: Go, Kubernetes, PostgreSQL. "
        "Nice to have: Python, AWS. You will design distributed systems and implement "
        "CI/CD pipelines for scalable microservices.",
    ),
    "partial match -> targeted/aggressive rewrite": (
        "Akhil Kumar, Software Engineer. Skills: Python, React, Flask, AWS. "
        "Experience: Software Dev at XYZ Corp (2022-2024) - Built REST APIs using Flask, "
        "Deployed services on AWS. Projects: ChatBot - Built using OpenAI API.",
        "Senior Backend Engineer at Acme Inc. Must have: Go, Kubernetes, PostgreSQL. "
        "Nice to have: Python, AWS. You will design distributed systems and implement "
        "CI/CD pipelines for scalable microservices.",
    ),
    "domain mismatch -> skip_mismatch": (
        "Akhil Kumar, Executive Chef. Skills: Menu design, French cuisine, kitchen management, "
        "food safety. Experience: Head Chef at Le Bistro (2018-2024) - Led a kitchen staff of 12, "
        "Designed seasonal tasting menus, Reduced food waste by 20%.",
        "Senior Backend Engineer at Acme Inc. Must have: Go, Kubernetes, PostgreSQL. "
        "Nice to have: Python, AWS. You will design distributed systems and implement "
        "CI/CD pipelines for scalable microservices.",
    ),
}


async def run_case(label: str, resume_text: str, jd_text: str) -> None:
    resume = await parse_resume(resume_text)
    jd = await analyze_jd(jd_text)
    gap_report = await detect_gaps(resume, jd)
    rewritten = await rewrite_bullets(resume, jd, gap_report)
    cover_letter = await generate_cover_letter(resume, jd, gap_report, rewritten)

    print(f"\n{'=' * 80}\nCASE: {label}\n{'=' * 80}")
    print(f"agent_strategy: {gap_report.agent_strategy}")
    print(f"agent_reasoning: {gap_report.agent_reasoning}")
    print(f"match_percentage: {gap_report.match_percentage}")

    if cover_letter is None:
        print("\n(no cover letter generated)")
        return

    print("\n--- Cover letter ---")
    print(cover_letter)


async def main() -> None:
    for label, (resume_text, jd_text) in CASES.items():
        await run_case(label, resume_text, jd_text)


if __name__ == "__main__":
    asyncio.run(main())
