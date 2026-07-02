# TailorAI — Project Plan & Architecture

## Problem Statement

**TailorAI** is an AI agent that takes a user's resume (PDF) and a job description, then autonomously decides the best strategy to optimize the application.

The agent runs a 5-stage prompt chain with structured JSON contracts between steps:

1. **Resume parsing** — extracts skills, experience, and projects from PDF using PyMuPDF
2. **JD analysis** — extracts required skills, responsibilities, and ATS keywords
3. **Gap detection** — compares resume vs JD, computes match percentage, identifies missing ATS keywords
4. **Bullet rewriting** — rewrites resume bullets optimized for the JD, shown side-by-side (original vs improved) with reasoning for each change
5. **Cover letter generation** — tailored per role using all prior context, strategy-aware based on match level

### What makes it agentic (not just a pipeline):

- **Self-healing parse** — if resume extraction is incomplete (empty skills, too few bullets), the agent retries with a more aggressive prompt strategy
- **Adaptive strategy** — based on match percentage, the agent decides rewrite aggressiveness:
  - Match > 85%: light keyword tweaks only
  - Match 40-85%: rewrite the weakest bullets
  - Match < 40%: full rewrite + "stretch role" warning
  - Completely different domain: skip rewriting, suggest user reconsider
- **Self-evaluation** — after generating outputs, the agent checks for hallucinations (cover letter mentioning skills not in resume, fabricated metrics in bullets) and re-runs the step if issues are found

**Tech Stack:** React.js (Vite), FastAPI, MongoDB Atlas (Motor async), Groq API (llama-3.3-70b-versatile), PyMuPDF, Python

---

## Folder Structure

```
tailorai/
├── CLAUDE.md
├── TAILORAI_PROJECT_PLAN.md
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry, CORS, lifespan
│   │   ├── config.py                # Env vars using pydantic-settings
│   │   ├── database.py              # Motor async client (MongoDB Atlas)
│   │   ├── models/
│   │   │   ├── session.py           # Pydantic models for session, JD, results
│   │   │   └── schemas.py           # Request/response schemas
│   │   ├── routes/
│   │   │   ├── upload.py            # POST /api/upload
│   │   │   ├── session.py           # GET /api/session/{id}
│   │   │   └── health.py            # GET /api/health
│   │   ├── services/
│   │   │   ├── pdf_parser.py        # PyMuPDF resume text extraction
│   │   │   ├── llm_client.py        # Groq API utility (call, parse, retry)
│   │   │   └── ai_chain.py          # The 5-step agentic prompt chain
│   │   └── prompts/
│   │       ├── step1_resume_parse.py
│   │       ├── step2_jd_analysis.py
│   │       ├── step3_gap_detection.py
│   │       ├── step4_bullet_rewrite.py
│   │       └── step5_cover_letter.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx         # Upload form
│   │   │   └── ResultsPage.jsx      # Dashboard with results
│   │   ├── components/
│   │   │   ├── ResumeUpload.jsx     # File upload + drag-drop
│   │   │   ├── JDInput.jsx          # JD text area
│   │   │   ├── GapReport.jsx        # Skill gap table
│   │   │   ├── BulletRewrite.jsx    # Side-by-side original vs rewritten
│   │   │   ├── CoverLetter.jsx      # Generated cover letter display
│   │   │   └── ProgressBar.jsx      # Step-by-step progress indicator
│   │   ├── services/
│   │   │   └── api.js               # Axios calls to backend
│   │   └── index.js
│   ├── package.json
│   └── .env
└── README.md
```

---

## Environment Variables

```
# .env.example
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/tailorai
GROQ_API_KEY=your_groq_api_key_here
FRONTEND_URL=http://localhost:5173
```

---

## MongoDB Schema (Atlas)

### Database: `tailorai`

### Collection: `sessions`

```json
{
  "_id": "ObjectId",
  "created_at": "datetime",
  "status": "processing | completed | failed",
  "current_step": 1,
  "current_step_name": "Parsing resume...",

  "resume_text": "raw extracted text from PDF",
  "resume_parsed": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "skills": ["Python", "React", "AWS"],
    "experience": [
      {
        "title": "Software Engineer",
        "company": "Company X",
        "duration": "2022-2024",
        "bullets": [
          "Built REST APIs using Flask...",
          "Deployed services on AWS..."
        ]
      }
    ],
    "education": [
      {
        "degree": "B.Tech CS",
        "institution": "ABC University",
        "year": "2022"
      }
    ],
    "projects": [
      {
        "name": "Project Name",
        "bullets": ["Built X using Y..."]
      }
    ]
  },

  "jd_raw": "full JD text pasted by user",
  "jd_parsed": {
    "title": "Senior Backend Engineer",
    "company": "Company Y",
    "required_skills": ["Go", "Kubernetes", "PostgreSQL"],
    "preferred_skills": ["Python", "AWS"],
    "key_responsibilities": ["Design distributed systems", "Build APIs"],
    "ats_keywords": [
      "microservices",
      "CI/CD",
      "distributed systems",
      "scalable"
    ]
  },

  "gap_report": {
    "matching_skills": ["Python", "AWS"],
    "missing_skills": ["Go", "Kubernetes", "PostgreSQL"],
    "match_percentage": 40,
    "ats_keywords_found": ["CI/CD"],
    "ats_keywords_missing": ["microservices", "distributed systems"],
    "agent_strategy": "aggressive_rewrite",
    "agent_reasoning": "Match is 40%, below threshold. Will rewrite all bullets."
  },

  "rewritten_bullets": [
    {
      "original": "Built REST APIs using Flask",
      "rewritten": "Designed and deployed 8+ RESTful microservices using Python and Flask, handling 5K+ daily requests with sub-200ms latency",
      "reason": "Added ATS keywords: microservices. Added quantifiable metrics. Made action verb stronger."
    }
  ],

  "cover_letter": "Dear Hiring Manager,...",

  "self_evaluation": {
    "passed": true,
    "issues_found": [],
    "re_runs": 0
  }
}
```

---

## API Endpoints

### `POST /api/upload`

**Request:** multipart/form-data

- `resume`: PDF file
- `job_description`: string (JD text)

**Response:**

```json
{
  "session_id": "abc123",
  "status": "processing",
  "message": "Analysis started"
}
```

**What it does:**

1. Extract text from PDF using PyMuPDF
2. Create session document in MongoDB with status "processing"
3. Kick off the AI chain as a BackgroundTask
4. Return session_id immediately

### `GET /api/session/{session_id}`

**Response:** The full session document (see schema above)

Frontend polls this every 2-3 seconds while status is "processing". The `current_step` and `current_step_name` fields update the progress bar.

### `GET /api/health`

Returns `{"status": "ok"}`

---

## AI Prompt Chain — Detailed Design

Each step outputs structured JSON. Each step receives the previous step's output as context. All prompts enforce JSON-only responses.

### Step 1: Resume Parsing

**Input:** Raw resume text (extracted by PyMuPDF)
**Output:** `resume_parsed` object
**Prompt strategy:** Extract name, email, skills (including implied ones from project descriptions), experience with bullets, education, projects. Provide the exact JSON schema in the prompt.

**Agentic self-healing:** After parsing, check:

- If `skills` array is empty → retry with prompt: "The resume doesn't have a clear skills section. Infer skills from the experience and project descriptions."
- If total bullet count < 3 → retry with prompt: "Extract more granular details from each experience entry. Break down responsibilities into individual bullet points."
- If extraction produced garbage (scanned PDF) → stop early, set status to "failed" with message "Could not extract text from this PDF. Please upload a text-based PDF."

### Step 2: JD Analysis

**Input:** Raw JD text
**Output:** `jd_parsed` object
**Prompt strategy:** Extract role title, company, required vs preferred skills, responsibilities, and ATS keywords. Capture both explicit skills ("Must know Python") and implicit ones ("build scalable systems" → distributed systems, scalability).

### Step 3: Gap Detection

**Input:** `resume_parsed` + `jd_parsed`
**Output:** `gap_report` object (including `agent_strategy` and `agent_reasoning`)
**Prompt strategy:** Compare skills, compute match percentage, identify missing ATS keywords.

**Agentic adaptive strategy:** The prompt asks the LLM to also decide the strategy:

- "Based on the match percentage, recommend one of: `light_tweaks` (>85%), `targeted_rewrite` (40-85%), `aggressive_rewrite` (<40%), or `skip_mismatch` (completely different domain). Explain your reasoning."
- The `agent_strategy` field drives Step 4's behavior.

### Step 4: Bullet Rewrite

**Input:** `resume_parsed` bullets + `jd_parsed` + `gap_report` (including `agent_strategy`)
**Output:** `rewritten_bullets` array
**Prompt strategy changes based on agent_strategy:**

- `light_tweaks`: "Only adjust wording to include these specific ATS keywords: [list]. Don't change the structure or add metrics."
- `targeted_rewrite`: "Identify the 3-5 weakest bullets and rewrite them. Add quantifiable metrics and incorporate missing ATS keywords naturally."
- `aggressive_rewrite`: "Rewrite ALL bullets. Add quantifiable metrics, incorporate ATS keywords, strengthen action verbs. Note: this is a stretch role for the candidate."
- `skip_mismatch`: Skip this step entirely. Set `rewritten_bullets` to empty array with a note.

Each rewritten bullet includes the `reason` explaining what changed and why.

### Step 5: Cover Letter Generation

**Input:** `resume_parsed` + `jd_parsed` + `gap_report`
**Output:** Cover letter string
**Prompt strategy changes based on match level:**

- High match (>85%): Emphasize direct fit, confidence
- Medium match (40-85%): Highlight matching skills, frame gaps as growth areas
- Low match (<40%): Lead with transferable skills, show enthusiasm for domain transition
- Mention company name and role title. Keep under 350 words.

### Self-Evaluation (runs after Step 5)

**Input:** All outputs (resume_parsed, rewritten_bullets, cover_letter)
**Output:** `self_evaluation` object
**Checks:**

- Does the cover letter mention any skill NOT in resume_parsed.skills or inferable from experience? → hallucination
- Do rewritten bullets contain fabricated specific numbers not in the original? → flag
- Does the cover letter reference the correct company name and role title?
- If issues found: re-run the offending step (max 1 re-run per step)

### Chain Execution Logic (ai_chain.py)

```python
async def run_chain(session_id: str, resume_text: str, jd_text: str):
    db = get_db()

    # Step 1: Parse resume
    await update_session(session_id, step=1, step_name="Parsing resume...")
    resume_parsed = await call_llm(STEP1_PROMPT, resume_text)

    # Agentic: self-healing parse
    if not resume_parsed.get("skills") or count_bullets(resume_parsed) < 3:
        resume_parsed = await call_llm(STEP1_AGGRESSIVE_PROMPT, resume_text)

    if is_garbage(resume_parsed):
        await fail_session(session_id, "Could not extract text from PDF")
        return

    await save_field(session_id, "resume_parsed", resume_parsed)

    # Step 2: Analyze JD
    await update_session(session_id, step=2, step_name="Analyzing job description...")
    jd_parsed = await call_llm(STEP2_PROMPT, jd_text)
    await save_field(session_id, "jd_parsed", jd_parsed)

    # Step 3: Gap detection + strategy decision
    await update_session(session_id, step=3, step_name="Detecting skill gaps...")
    gap_report = await call_llm(STEP3_PROMPT, resume_parsed, jd_parsed)
    await save_field(session_id, "gap_report", gap_report)

    # Step 4: Bullet rewrite (strategy-aware)
    strategy = gap_report.get("agent_strategy", "targeted_rewrite")

    if strategy != "skip_mismatch":
        await update_session(session_id, step=4, step_name="Rewriting resume bullets...")
        rewritten = await call_llm(
            get_rewrite_prompt(strategy),
            resume_parsed, jd_parsed, gap_report
        )
        await save_field(session_id, "rewritten_bullets", rewritten)
    else:
        await save_field(session_id, "rewritten_bullets", [])

    # Step 5: Cover letter
    await update_session(session_id, step=5, step_name="Generating cover letter...")
    cover_letter = await call_llm(STEP5_PROMPT, resume_parsed, jd_parsed, gap_report)
    await save_field(session_id, "cover_letter", cover_letter)

    # Agentic: self-evaluation
    evaluation = await self_evaluate(resume_parsed, rewritten, cover_letter, jd_parsed)
    if not evaluation["passed"] and evaluation["re_runs"] == 0:
        if "cover_letter_hallucination" in evaluation["issues_found"]:
            cover_letter = await call_llm(STEP5_PROMPT, resume_parsed, jd_parsed, gap_report)
            await save_field(session_id, "cover_letter", cover_letter)
        evaluation["re_runs"] = 1

    await save_field(session_id, "self_evaluation", evaluation)
    await update_session(session_id, status="completed")
```

---

## Frontend Pages

### HomePage

- Drag-and-drop or click-to-upload for resume PDF
- Single JD text area (expandable)
- "Analyze" button → POST /api/upload → redirect to ResultsPage

### ResultsPage

- Progress bar with 5 steps, showing current step name
- Once complete, 3 sections:
  1. **Gap Report** — matching skills (green), missing skills (red), match %, ATS keyword checklist, agent strategy badge
  2. **Bullet Rewrites** — two-column: "Original" left, "Optimized" right, reason below each pair, copy button per bullet
  3. **Cover Letter** — rendered text with copy-to-clipboard button

---

## Build Order

### Phase 1: Backend skeleton

1. Project setup, folder structure, requirements.txt, .env.example
2. config.py, database.py (Motor + Atlas), main.py (FastAPI + CORS + lifespan)
3. GET /api/health
4. PDF parser with edge case handling
5. Pydantic models matching MongoDB schema
6. POST /api/upload (no AI, just save and return session_id)
7. GET /api/session/{id}

### Phase 2: AI prompt chain

1. Groq client utility (call, parse JSON, retry)
2. Step 1 prompt (resume parsing + self-healing)
3. Step 2 prompt (JD analysis)
4. Step 3 prompt (gap detection + strategy decision)
5. Step 4 prompt (bullet rewrite, strategy-aware)
6. Step 5 prompt (cover letter, match-level-aware)
7. Self-evaluation check
8. Wire chain as BackgroundTask

### Phase 3: Frontend

1. Vite + React setup
2. api.js (Axios)
3. HomePage (upload + JD input)
4. ResultsPage (polling + progress bar)
5. GapReport, BulletRewrite, CoverLetter components

### Phase 4: Polish + multi-JD

1. Error handling
2. Loading states and UX
3. Multi-JD support (loop chain, tabs on results)
4. README with setup instructions

---

## Key Implementation Notes

- **MongoDB Atlas:** Connection string from Atlas dashboard. Whitelist IP or 0.0.0.0/0 for dev.
- **Groq model:** `llama-3.3-70b-versatile` via `groq` package.
- **JSON enforcement:** Every prompt ends with "Respond ONLY with valid JSON. No markdown, no explanation, no code fences."
- **Background task:** FastAPI `BackgroundTasks` — upload returns immediately.
- **CORS:** Allow `http://localhost:5173` (Vite default).
- **PyMuPDF:** `pip install PyMuPDF` (imports as `fitz`).
- **Error recovery:** Retry Groq calls once. On second failure, set session status to "failed".
- **Polling:** Frontend polls every 2 seconds. Stop on "completed" or "failed".
