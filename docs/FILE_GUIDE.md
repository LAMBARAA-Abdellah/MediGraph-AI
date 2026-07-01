# MediGraph AI — Complete File Guide

This document explains every file in the project, its purpose, and key sections.

---

## Root Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start, API summary |
| `docker-compose.yml` | Multi-service orchestration (backend, MCP, frontend, Redis) |
| `Dockerfile` | Multi-stage build for backend + frontend |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template (never commit `.env`) |
| `.gitignore` | Git ignore rules |
| `langgraph.json` | LangGraph Studio configuration |
| `pyproject.toml` | Python project metadata and pytest config |
| `streamlit_demo.py` | Optional Streamlit demo interface |

---

## Backend (`backend/app/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package init, version info |
| `config.py` | Pydantic Settings — all env vars, singleton via `get_settings()` |
| `state.py` | `MedicalState` TypedDict — shared LangGraph state with MessagesState |
| `graph.py` | StateGraph definition, conditional edges, checkpoint, interrupt |
| `api.py` | FastAPI app — all REST endpoints, CORS, middleware |
| `database.py` | SQLAlchemy engine, ORM models, `init_db()` |
| `models.py` | Re-exports ORM models for clean architecture |
| `schemas.py` | Pydantic request/response validation schemas |

### Nodes (`backend/app/nodes/`)

| File | Purpose |
|------|---------|
| `supervisor.py` | Supervisor Agent — routing, error handling, conditional edges |
| `diagnostic_agent.py` | Diagnostic Agent — 5 questions, summary, recommendation |
| `physician_review.py` | Human-in-the-Loop — pause, approve/reject, resume |
| `report_agent.py` | Report Agent — JSON, Markdown, HTML, PDF generation |

### Tools (`backend/app/tools/`)

| File | Purpose |
|------|---------|
| `patient_tools.py` | `ask_patient`, `collect_patient_information`, `generate_clinical_summary` |
| `recommendation_tools.py` | `recommend_intermediate_care` — safe recommendations only |
| `medical_tools.py` | Medical knowledge lookup, drug database demo, red flags |
| `mcp_client.py` | MCP HTTP client with local fallback |

### Services (`backend/app/services/`)

| File | Purpose |
|------|---------|
| `consultation_service.py` | Business logic — session, consultation, review, report |

### Other Backend

| File | Purpose |
|------|---------|
| `prompts/__init__.py` | LLM prompt templates for all agents |
| `middleware/logging_middleware.py` | Structlog setup, execution timing, node transition logging |
| `memory/session_memory.py` | In-memory + optional Redis session store |

---

## MCP Server (`mcp_server/`)

| File | Purpose |
|------|---------|
| `server.py` | FastAPI MCP HTTP server — `/tools`, `/health` |
| `tools.py` | Tool registry — patient, recommendation, medical, calendar |

---

## Frontend (`frontend/`)

| File | Purpose |
|------|---------|
| `package.json` | React + Vite dependencies |
| `vite.config.js` | Dev server, API proxy |
| `src/App.jsx` | Router, sidebar navigation |
| `src/services/api.js` | Axios API client |
| `src/pages/Dashboard.jsx` | System overview, metrics |
| `src/pages/PatientRegistration.jsx` | Patient intake form |
| `src/pages/Consultation.jsx` | Start consultation |
| `src/pages/Questionnaire.jsx` | 5-question UI with progress |
| `src/pages/PhysicianReview.jsx` | HITL approve/reject |
| `src/pages/Reports.jsx` | Report viewer + PDF export |
| `src/pages/ConsultationHistory.jsx` | Session history |
| `src/pages/Settings.jsx` | App configuration |

---

## Tests (`backend/tests/`)

| File | Purpose |
|------|---------|
| `conftest.py` | Pytest fixtures — 3 test cases |
| `test_workflow.py` | Case 1 (respiratory), Case 2 (red flags), Case 3 (benign) |

---

## Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `INSTALLATION.md` | Setup instructions |
| `DEVELOPER_GUIDE.md` | Development workflow |
| `API.md` | REST API reference |
| `ARCHITECTURE.md` | Clean architecture, SOLID |
| `diagrams/DIAGRAMS.md` | Mermaid architecture/workflow/sequence/state/class diagrams |
| `reports/ACADEMIC_REPORT.md` | Full academic project report |

---

## Scripts

| File | Purpose |
|------|---------|
| `scripts/generate_presentation.py` | Generates 27-slide PowerPoint |

---

*This system does not replace a professional medical consultation.*
