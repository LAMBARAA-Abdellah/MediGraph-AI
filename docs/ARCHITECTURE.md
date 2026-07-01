# Architecture Documentation

## Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│         React Frontend  │  FastAPI REST API             │
├─────────────────────────────────────────────────────────┤
│                    Application Layer                     │
│    ConsultationService  │  LangGraph Workflow           │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                         │
│   MedicalState  │  Agent Nodes  │  Tools  │  Prompts   │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│   SQLite  │  MCP Server  │  Redis  │  Checkpointer     │
└─────────────────────────────────────────────────────────┘
```

## Multi-Agent System

### Supervisor Agent
- Entry point for workflow
- Conditional routing based on `consultation_status`
- Error handling and graph transitions

### Diagnostic Agent
- Asks exactly 5 sequential questions via `ask_patient` tool
- Records answers via `record_patient_answer`
- Generates Clinical Summary via `generate_clinical_summary`
- Generates Intermediate Recommendation via `recommend_intermediate_care`

### Physician Review Agent
- Human-in-the-Loop interrupt point
- Workflow pauses until API receives review
- Physician can approve, reject, modify recommendations

### Report Agent
- Generates structured reports in 4 formats
- Includes mandatory disclaimer
- Persists to database and filesystem

## State Management

`MedicalState` TypedDict with:
- `messages` — LangGraph MessagesState (add_messages reducer)
- `patient_information` — Demographics
- `question_count` / `patient_answers` — Questionnaire data
- `clinical_summary` / `intermediate_recommendation` — Clinical outputs
- `physician_review` / `physician_treatment` — HITL data
- `final_report` — Generated reports
- `consultation_status` — Workflow status

## Persistence

- **SQLite** — Patient, Consultation, Question, Answer, Report, PhysicianReview
- **LangGraph Checkpointer** — Workflow state persistence (SQLite)
- **Redis** (optional) — Session cache

## MCP Integration

MCP Server exposes tools via HTTP:
- Patient tools (collect, ask, record, summarize)
- Recommendation tools
- Medical knowledge lookup
- Drug database demo
- Calendar/appointment scheduling

MCP Client in LangGraph falls back to local tools if server unavailable.

## SOLID Principles

| Principle | Implementation |
|-----------|---------------|
| Single Responsibility | Each node/service has one purpose |
| Open/Closed | Tools extensible via MCP registry |
| Liskov Substitution | MCP client falls back to local tools |
| Interface Segregation | Pydantic schemas per endpoint |
| Dependency Inversion | Settings via `get_settings()`, DI in services |

## Security Considerations

- No hardcoded API keys (environment variables)
- Medical disclaimer on all outputs
- No medication prescription
- Educational use only

*This system does not replace a professional medical consultation.*
