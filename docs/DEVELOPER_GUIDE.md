# Developer Guide

## Adding a New Agent Node

1. Create node file in `backend/app/nodes/`
2. Implement node function: `def my_node(state: MedicalState) -> dict`
3. Add routing function if conditional edges needed
4. Register in `backend/app/graph.py`
5. Update supervisor routing logic

## Adding a New Tool

1. Create tool with `@tool` decorator in `backend/app/tools/`
2. Register in `backend/app/tools/__init__.py` → `ALL_TOOLS`
3. Add to MCP server in `mcp_server/tools.py` → `MCP_TOOLS`
4. Write tests in `backend/tests/`

## Running Tests

```bash
pytest backend/tests/ -v --cov=backend
```

## Code Style

- PEP 8 compliance
- Type hints on all functions
- Docstrings on public methods
- No hardcoded secrets

## LangGraph Debugging

```bash
langgraph dev
```

Use LangGraph Studio to visualize:
- Node transitions
- State snapshots
- Interrupt points (physician_review)

## Database Migrations

Currently uses `Base.metadata.create_all()`. For production, integrate Alembic.

## Environment Variables

See `.env.example` for all configurable settings.

## Logging

Structured logging via `structlog`:

```python
from backend.app.middleware.logging_middleware import get_logger
logger = get_logger("my.module")
logger.info("event_name", key="value")
```

Tracked events:
- Execution time
- Node transitions
- LLM calls
- Tool calls
- HTTP requests
