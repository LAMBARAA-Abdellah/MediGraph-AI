# MediGraph AI
## Overview

MediGraph AI simulates an academic clinical workflow using multiple AI agents coordinated through LangGraph. The platform provides **Preliminary Clinical Orientation**, **Clinical Summary**, and **Intermediate Recommendation** — never medical diagnosis.

### Key Features

- **Supervisor Agent** — Workflow orchestration and routing
- **Diagnostic Agent** — 5 sequential questions, clinical summary generation
- **Physician Review Agent** — Human-in-the-Loop workflow pause
- **Report Agent** — JSON, Markdown, HTML, and PDF reports
- **MCP Integration** — Model Context Protocol tool server
- **FastAPI REST API** — Production-ready backend
- **React Frontend** — Full clinical workflow UI
- **LangGraph Studio** — Graph visualization and debugging
- **SQLite Persistence** — Consultations, Q&A, reports
- **Docker Compose** — One-command deployment

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   React     │────▶│   FastAPI    │────▶│   LangGraph     │
│  Frontend   │     │   Backend    │     │   Workflow      │
└─────────────┘     └──────────────┘     └────────┬────────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │   SQLite     │     │  MCP Server     │
                    │   Database   │     │  (Tools)        │
                    └──────────────┘     └─────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.12
- Node.js 20+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone and enter project
cd MediGraph-AI

# Copy environment config
cp .env.example .env

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize and run backend
set PYTHONPATH=.  # Windows
export PYTHONPATH=.  # Linux/Mac
uvicorn backend.app.api:app --reload --port 8000

# MCP Server (separate terminal)
uvicorn mcp_server.server:app --port 8100

# Frontend
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

Services:
- Backend API: http://localhost:8000
- MCP Server: http://localhost:8100
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

## LangGraph Studio

```bash
pip install langgraph-cli
langgraph dev
```

Configuration: `langgraph.json`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/metrics` | Business metrics |
| POST | `/sessions/start` | Start patient session |
| POST | `/consultation/start` | Start questionnaire |
| POST | `/consultation/answer` | Submit answer |
| POST | `/consultation/physician-review` | Physician review |
| POST | `/consultation/resume` | Resume workflow |
| GET | `/consultation/{thread_id}` | Get state |
| GET | `/consultation/{thread_id}/report` | Get report |

---

## Workflow

1. **Patient Registration** → Collect demographics
2. **Diagnostic Agent** → Ask 5 sequential questions
3. **Clinical Summary** → Generate orientation summary
4. **Intermediate Recommendation** → Safe care guidance
5. **Physician Review** → Human-in-the-Loop (interrupt)
6. **Report Agent** → Generate final report

---

## Testing

```bash
pytest backend/tests/ -v
```

Test cases:
- Case 1: Simple Respiratory Syndrome
- Case 2: Red Flags
- Case 3: Benign Case

---

## Project Structure

```
MediGraph-AI/
├── backend/app/          # FastAPI + LangGraph application
│   ├── graph.py          # StateGraph definition
│   ├── state.py          # MedicalState TypedDict
│   ├── api.py            # REST endpoints
│   ├── nodes/            # Agent nodes
│   ├── tools/            # LangChain tools
│   ├── services/         # Business logic
│   └── tests/            # Pytest tests
├── mcp_server/           # MCP tool server
├── frontend/             # React application
├── docs/                 # Documentation
├── docker-compose.yml
├── Dockerfile
└── langgraph.json
```

---

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Academic Report](docs/reports/ACADEMIC_REPORT.md)
- [Diagrams](docs/diagrams/)

---

## License

Academic project — Université Mohammed VI Polytechnique, Master BDCC.

---

*This system does not replace a professional medical consultation.*
