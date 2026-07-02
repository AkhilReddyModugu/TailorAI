# TailorAI - AI-Powered Job Application Agent

## Project Overview

AI agent that takes a resume (PDF) + job description, runs a 5-stage
prompt chain with agentic decision points, and outputs: skill gap report,
ATS keyword analysis, rewritten resume bullets (side-by-side diff), and
tailored cover letter.

## Tech Stack

- Backend: FastAPI, Python 3.11+
- Database: MongoDB Atlas with Motor (async)
- AI: Groq API (llama-3.3-70b-versatile)
- PDF: PyMuPDF (imports as fitz)
- Frontend: React.js with Vite
- HTTP: Axios

## Code Style

- async/await everywhere in backend, no sync DB calls
- Pydantic models for all request/response schemas
- Type hints on all Python functions
- All LLM prompts enforce JSON-only output
- React functional components with hooks only
- try/except on all LLM calls with 1 retry

## Agentic Decision Points (IMPORTANT)

1. Self-healing parse: after resume parsing, if skills=[] or bullets<3, retry with aggressive prompt
2. Adaptive strategy: after gap detection, choose rewrite aggressiveness based on match%
   - > 85%: light keyword tweaks only
   - 40-85%: rewrite weakest bullets
   - <40%: full rewrite + "stretch role" warning
   - Different domain entirely: skip rewrite, suggest user reconsider
3. Self-evaluation: after all outputs, check for hallucinations and re-run if found

## Verification

- After any endpoint: show curl command and run it
- After any prompt step: run with sample data, show actual JSON output
- After frontend changes: confirm renders without console errors
- After chain wiring: test full end-to-end flow

## Environment Variables

- MONGO_URI (MongoDB Atlas connection string)
- GROQ_API_KEY
- FRONTEND_URL (http://localhost:5173)
