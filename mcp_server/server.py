"""MCP Server HTTP API for MediGraph AI tool exposure."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mcp_server.tools import execute_tool, list_tools

app = FastAPI(
    title="MediGraph MCP Server",
    description="MCP tool server for MediGraph AI clinical orientation system",
    version="1.0.0",
)


class ToolRequest(BaseModel):
    """MCP tool execution request."""

    arguments: Dict[str, Any] = {}


class ToolResponse(BaseModel):
    """MCP tool execution response."""

    result: Any = None
    tool: str = ""
    status: str = "success"
    error: str = ""


@app.get("/health")
async def health():
    """MCP server health check."""
    return {"status": "healthy", "service": "medigraph-mcp-server"}


@app.get("/tools")
async def get_tools():
    """List available MCP tools."""
    return {
        "tools": list_tools(),
        "count": len(list_tools()),
        "description": "MediGraph AI MCP Tools - Educational clinical orientation only",
    }


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolRequest):
    """
    Execute an MCP tool.

    Available tools:
    - collect_patient_information
    - ask_patient
    - record_patient_answer
    - generate_clinical_summary
    - recommend_intermediate_care
    - lookup_medical_knowledge
    - lookup_drug_database
    - check_red_flags
    - schedule_appointment
    """
    result = execute_tool(tool_name, request.arguments)

    if result.get("status") == "failed":
        raise HTTPException(status_code=400, detail=result.get("error", "Tool execution failed"))

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
