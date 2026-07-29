# AI-Powered Customer Complaint Management System

A pharmaceutical (API & FDF) customer complaint intake tool: a QA reviewer drops
in a complaint document (or pastes an email), and a LangGraph agent pipeline
running on Groq extracts structured fields, assesses risk, checks completeness,
flags duplicates, and suggests root cause / CAPA — auto-populating the
"Log Customer Complaint" form shown in the reference UI.

## Architecture

```
┌─────────────────────┐        ┌──────────────────────┐        ┌──────────────────┐
│  React + Redux SPA  │  HTTP  │   FastAPI backend      │  calls │  Groq API         │
│  (Log Complaint form│ ─────► │   /api/ai/ingest/*      │ ─────► │  gemma2-9b-it     │
│   + AI Assistant)   │ ◄───── │   /api/ai/chat          │ ◄───── │  llama-3.3-70b    │
└─────────────────────┘        │   /api/complaints        │        └──────────────────┘
                                │        │                │
                                │        ▼                │
                                │  LangGraph StateGraph   │
                                │  (agents/graph.py)      │
                                │        │                │
                                │        ▼                │
                                │  Postgres / MySQL       │
                                └──────────────────────────┘
```

### Why this structure

- **FastAPI** exposes two route groups: `routes_ai.py` (the AI-driven intake +
  chat) and `routes_complaints.py` (plain CRUD once a complaint exists).
- **LangGraph** (`app/agents/graph.py`) is a linear `StateGraph` with one node
  per AI capability, so each capability is independently testable and it's
  obvious where to add branching later (e.g. skip CAPA suggestion for Minor
  severity complaints):

  ```
  extract_fields → check_completeness → classify_risk
                 → detect_duplicates → suggest_root_cause_and_capa
                 → summarize_and_respond
  ```

- **Two Groq models are used deliberately**: `gemma2-9b-it` for the cheap/fast
  first-pass field extraction and per-turn summaries, `llama-3.3-70b-versatile`
  for the heavier reasoning steps (risk classification, duplicate comparison,
  root cause/CAPA, and the free-form chat) where better instruction-following
  matters more than latency.
- **Redux** holds two slices: `complaintSlice` (the form's field values +
  ingest/save status — this is what "Awaiting AI extraction..." vs a filled,
  highlighted field is driven by) and `assistantSlice` (the chat transcript).

## End-to-end workflow (what happens on drag & drop)

1. User drops a PDF/DOCX/TXT/EML on the **AI Complaint Intake Assistant**
   panel → `FileUpload.jsx` dispatches `ingestDocument(file)`.
2. Redux thunk calls `POST /api/ai/ingest/document` (multipart) →
   `routes_ai.py`.
3. `document_parser.py` extracts raw text (pypdf / python-docx / stdlib
   `email` module depending on file type).
4. `intake_graph.invoke({...})` runs the LangGraph pipeline described above.
5. The backend persists a new `Complaint` row with everything the graph
   produced and returns `{ complaint_id, extracted, analysis, assistant_message }`.
6. Redux's `applyIngestResult` reducer merges `extracted` into `fields` —
   every `FormField` reading that field re-renders from "Awaiting AI
   extraction..." to the filled, light-blue-highlighted value.
7. The `analysis` block (completeness %, root cause, CAPA, duplicate flag)
   renders under the progress bar, and `assistant_message` appears as the
   first assistant chat bubble.
8. Reviewer can edit any field directly (plain controlled inputs), ask the
   assistant follow-up questions (`POST /api/ai/chat`, grounded on the
   complaint's current DB row), and click **Save Complaint**
   (`PUT /api/complaints/{id}`) which flips status to "Under Review".

## Bonus AI features implemented

| Feature | Where |
|---|---|
| Complaint Completeness Checker | `nodes.check_completeness` — flags which of the 10 required fields the LLM couldn't find |
| AI Risk Classification | `nodes.classify_risk` — Severity/Priority with reasoning, based on patient-safety impact |
| Duplicate Complaint Detection | `nodes.detect_duplicates` — compares against the last 50 complaints in the DB |
| Root Cause Recommendation | `nodes.suggest_root_cause_and_capa` |
| CAPA Recommendation | same node, paired output |
| Complaint Summary | `nodes.summarize_and_respond` |
| Follow-up chat grounded on the record | `POST /api/ai/chat` |

## Setup

### 1. Database
Create an empty Postgres or MySQL database, e.g.:
```bash
createdb complaint_qms   # Postgres
```
Tables are auto-created on first backend startup (see `app/main.py`) — no
migration step needed for this assignment.

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # then fill in GROQ_API_KEY and DATABASE_URL
uvicorn app.main:app --reload --port 8000
```
Get a free Groq API key at https://console.groq.com/keys.

### 3. Frontend
```bash
cd frontend
npm install
npm run dev     # http://localhost:5173, proxies /api to :8000
```

### 4. Try it
Use the sample documents in `backend/sample_data/` (a contamination email,
a packaging-defect email, and a discoloration PDF) — drag one onto the AI
Assistant panel, or paste its contents into "Paste Complaint Text / Email".

## Notes on scope

- OCR/document parsing is intentionally simple (pypdf / python-docx / stdlib
  `email`), per the assignment — no production-grade parsing.
- DB migrations use `Base.metadata.create_all` rather than Alembic, to keep
  setup to one command for this assignment.
- Auth is out of scope — every reviewer sees the same shared complaint list.
