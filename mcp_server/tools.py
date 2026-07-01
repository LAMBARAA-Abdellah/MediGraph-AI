"""MCP Server tools - exposed via HTTP API for LangGraph integration."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import local tool implementations
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

# Demo calendar/appointment data
APPOINTMENT_SLOTS = [
    {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "time": "09:00", "available": True},
    {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "time": "10:30", "available": True},
    {"date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), "time": "14:00", "available": True},
    {"date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "time": "11:00", "available": False},
]


def schedule_appointment(patient_name: str, preferred_date: str = "", notes: str = "") -> Dict[str, Any]:
    """
    Demo calendar tool - schedule a consultation appointment.

    Args:
        patient_name: Patient name
        preferred_date: Preferred appointment date (YYYY-MM-DD)
        notes: Additional notes

    Returns:
        Appointment scheduling result
    """
    available_slots = [s for s in APPOINTMENT_SLOTS if s["available"]]

    if preferred_date:
        matching = [s for s in available_slots if s["date"] == preferred_date]
        if matching:
            slot = matching[0]
        else:
            slot = available_slots[0] if available_slots else None
    else:
        slot = available_slots[0] if available_slots else None

    if not slot:
        return {
            "scheduled": False,
            "message": "No available appointment slots",
        }

    return {
        "scheduled": True,
        "appointment": {
            "patient_name": patient_name,
            "date": slot["date"],
            "time": slot["time"],
            "location": "MediGraph Demo Clinic",
            "notes": notes,
        },
        "message": f"Appointment scheduled for {slot['date']} at {slot['time']}",
        "disclaimer": "This system does not replace a professional medical consultation.",
    }


# Tool registry mapping tool names to functions
MCP_TOOLS = {
    "collect_patient_information": lambda args: collect_patient_information.invoke(args),
    "ask_patient": lambda args: ask_patient.invoke(args),
    "record_patient_answer": lambda args: record_patient_answer.invoke(args),
    "generate_clinical_summary": lambda args: generate_clinical_summary.invoke(args),
    "recommend_intermediate_care": lambda args: recommend_intermediate_care.invoke(args),
    "lookup_medical_knowledge": lambda args: lookup_medical_knowledge.invoke(args),
    "lookup_drug_database": lambda args: lookup_drug_database.invoke(args),
    "check_red_flags": lambda args: check_red_flags.invoke(args),
    "schedule_appointment": lambda args: schedule_appointment(**args),
}


def list_tools() -> List[str]:
    """List all available MCP tools."""
    return list(MCP_TOOLS.keys())


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an MCP tool by name.

    Args:
        tool_name: Tool identifier
        arguments: Tool arguments

    Returns:
        Tool execution result
    """
    tool_fn = MCP_TOOLS.get(tool_name)
    if not tool_fn:
        return {"error": f"Unknown tool: {tool_name}", "available_tools": list_tools()}

    try:
        result = tool_fn(arguments)
        return {"result": result, "tool": tool_name, "status": "success"}
    except Exception as e:
        return {"error": str(e), "tool": tool_name, "status": "failed"}
