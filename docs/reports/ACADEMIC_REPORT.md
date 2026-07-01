# MediGraph AI — Academic Project Report

**Intelligent Multi-Agent Clinical Orientation System**

Université Mohammed VI Polytechnique — Master BDCC  
Date: July 2026

---

## 1. Introduction

MediGraph AI is an educational multi-agent system that simulates a clinical orientation workflow using modern AI orchestration frameworks. The system demonstrates how LangGraph, LangChain, FastAPI, and MCP can be combined to create a production-ready, modular clinical orientation platform.

**Important:** This system provides Preliminary Clinical Orientation only. It does NOT provide medical diagnosis and does NOT replace healthcare professionals.

*Disclaimer: This system does not replace a professional medical consultation.*

---

## 2. Clinical Workflow

The simulated workflow follows these steps:

1. **Patient Registration** — Collect name, age, gender, medical history, chief complaint
2. **Diagnostic Questionnaire** — Exactly 5 sequential questions via Diagnostic Agent
3. **Clinical Summary** — Educational orientation summary (not diagnosis)
4. **Intermediate Recommendation** — Safe care guidance (rest, hydration, consultation)
5. **Physician Review** — Human-in-the-Loop approval/modification
6. **Final Report** — Structured output in JSON, Markdown, HTML, and PDF

---

## 3. LangGraph Implementation

LangGraph provides the orchestration backbone:

- **StateGraph** with `MedicalState` TypedDict
- **Conditional edges** for dynamic routing
- **Checkpoint persistence** via SQLite checkpointer
- **Interrupt before** `physician_review` for Human-in-the-Loop
- **MessagesState** pattern with `add_messages` reducer

Graph nodes: Supervisor → Diagnostic Agent → Physician Review → Report Agent

---

## 4. LangChain Integration

LangChain tools power agent capabilities:

| Tool | Purpose |
|------|---------|
| `collect_patient_information` | Patient intake |
| `ask_patient` | Sequential questions |
| `record_patient_answer` | Answer storage |
| `generate_clinical_summary` | Summary generation |
| `recommend_intermediate_care` | Safe recommendations |

All tools include the mandatory medical disclaimer.

---

## 5. MCP (Model Context Protocol)

A dedicated MCP server exposes tools via HTTP API:

- Patient tools
- Recommendation tools
- Medical knowledge lookup
- Drug database demo
- Calendar/appointment scheduling

The MCP client in LangGraph falls back to local tools when the server is unavailable.

---

## 6. FastAPI Backend

REST API endpoints:

- Session management
- Consultation workflow
- Physician review submission
- Report retrieval
- Health checks and metrics

Features: Pydantic validation, CORS, structured logging, Prometheus metrics, dependency injection.

---

## 7. Frontend

React application with pages:

- Dashboard, Patient Registration, Consultation
- Questionnaire (progress bar, Q&A)
- Physician Review (approve/reject)
- Reports (export PDF)
- Settings, History

---

## 8. Architecture

Clean architecture with four layers:

1. **Presentation** — React + FastAPI
2. **Application** — ConsultationService + LangGraph
3. **Domain** — State, Nodes, Tools, Prompts
4. **Infrastructure** — SQLite, MCP, Redis, Checkpointer

SOLID principles applied throughout.

---

## 9. Implementation Details

- Python 3.12, PEP 8, type hints, docstrings
- SQLAlchemy ORM with 6 database tables
- ReportLab for PDF generation
- Jinja2 for HTML reports
- Docker Compose for deployment
- LangGraph Studio configuration

---

## 10. Testing

Three test scenarios implemented:

| Case | Description | Verification |
|------|-------------|-------------|
| Case 1 | Simple Respiratory Syndrome | 5 questions, summary, recommendation |
| Case 2 | Red Flags | High urgency detection |
| Case 3 | Benign Case | Routine care level |

All tests verify disclaimer presence and no medication prescription.

---

## 11. Results

The system successfully:

- Orchestrates 4 agents through LangGraph
- Asks exactly 5 sequential questions
- Generates Clinical Summary and Intermediate Recommendation
- Pauses for physician Human-in-the-Loop review
- Produces multi-format reports with disclaimer
- Integrates MCP tools with fallback
- Provides full REST API and React UI

---

## 12. Conclusion

MediGraph AI demonstrates a complete, production-ready architecture for multi-agent clinical orientation systems. The project showcases best practices in AI agent orchestration, clean architecture, and responsible AI design for healthcare education.

---

## 13. Future Improvements

- Integration with real EHR systems
- Multi-language support
- Advanced LLM-powered summary generation
- Alembic database migrations
- Kubernetes deployment
- Real-time WebSocket updates
- Enhanced security (OAuth2, RBAC)
- FHIR compliance for healthcare interoperability

---

*This system does not replace a professional medical consultation.*
