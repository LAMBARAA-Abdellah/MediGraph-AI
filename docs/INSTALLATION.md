# Installation Guide

## System Requirements

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| Node.js | 20+ |
| Docker | 24+ (optional) |
| Redis | 7+ (optional) |

## Local Development Setup

### 1. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and set your `OPENAI_API_KEY` (optional — system works with rule-based tools).

### 2. Python Backend

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

Set Python path:

```bash
# Windows PowerShell
$env:PYTHONPATH = "."

# Linux/macOS
export PYTHONPATH=.
```

Create data directories:

```bash
mkdir data logs reports data/checkpoints
```

Start backend:

```bash
uvicorn backend.app.api:app --reload --host 0.0.0.0 --port 8000
```

### 3. MCP Server

```bash
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8100
```

### 4. React Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 5. LangGraph Studio

```bash
pip install langgraph-cli
langgraph dev
```

### 6. Streamlit Demo (Optional)

```bash
streamlit run streamlit_demo.py
```

## Docker Deployment

```bash
docker-compose up --build -d
```

With Redis:

```bash
docker-compose --profile with-redis up --build -d
```

## Verification

```bash
curl http://localhost:8000/health
curl http://localhost:8100/health
pytest backend/tests/ -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Set `PYTHONPATH=.` from project root |
| Database locked | Ensure single backend instance |
| CORS errors | Add frontend URL to `CORS_ORIGINS` in `.env` |
| MCP unavailable | System falls back to local tools automatically |
