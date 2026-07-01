"""MCP Client for integrating MCP server tools into LangGraph workflow."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger, log_tool_call

logger = get_logger("tools.mcp_client")


class MCPClient:
    """
    Client for communicating with the MediGraph MCP Server.

    Provides async methods to invoke MCP tools from LangGraph nodes.
    Falls back to local tool implementations if MCP server is unavailable.
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.mcp_server_url
        self.timeout = 30.0
        self._available = None

    async def health_check(self) -> bool:
        """Check if MCP server is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                self._available = response.status_code == 200
                return self._available
        except Exception as e:
            logger.warning("mcp_server_unavailable", error=str(e))
            self._available = False
            return False

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via HTTP API.

        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        log_tool_call(logger, f"mcp_{tool_name}", **arguments)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/tools/{tool_name}",
                    json=arguments,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("mcp_call_failed", tool=tool_name, error=str(e))
            return await self._fallback_tool(tool_name, arguments)

    async def _fallback_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to local tool implementations when MCP server is unavailable."""
        logger.info("mcp_fallback", tool=tool_name)

        from backend.app.tools.medical_tools import (
            check_red_flags,
            lookup_drug_database,
            lookup_medical_knowledge,
        )
        from backend.app.tools.patient_tools import (
            ask_patient,
            collect_patient_information,
            generate_clinical_summary,
            record_patient_answer,
        )
        from backend.app.tools.recommendation_tools import recommend_intermediate_care

        local_tools = {
            "collect_patient_information": collect_patient_information,
            "ask_patient": ask_patient,
            "record_patient_answer": record_patient_answer,
            "generate_clinical_summary": generate_clinical_summary,
            "recommend_intermediate_care": recommend_intermediate_care,
            "lookup_medical_knowledge": lookup_medical_knowledge,
            "lookup_drug_database": lookup_drug_database,
            "check_red_flags": check_red_flags,
        }

        tool_fn = local_tools.get(tool_name)
        if tool_fn:
            result = tool_fn.invoke(arguments)
            return {"result": result, "source": "local_fallback"}
        return {"error": f"Unknown tool: {tool_name}", "source": "local_fallback"}

    async def list_tools(self) -> List[str]:
        """List available MCP tools."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/tools")
                response.raise_for_status()
                data = response.json()
                return data.get("tools", [])
        except Exception:
            return [
                "collect_patient_information",
                "ask_patient",
                "record_patient_answer",
                "generate_clinical_summary",
                "recommend_intermediate_care",
                "lookup_medical_knowledge",
                "lookup_drug_database",
                "check_red_flags",
                "schedule_appointment",
            ]


# Singleton MCP client
mcp_client = MCPClient()


def run_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for MCP tool calls."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    mcp_client.call_tool(tool_name, arguments),
                )
                return future.result(timeout=30)
        return loop.run_until_complete(mcp_client.call_tool(tool_name, arguments))
    except RuntimeError:
        return asyncio.run(mcp_client.call_tool(tool_name, arguments))
