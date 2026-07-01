"""LangChain tools package for MediGraph AI."""

from backend.app.tools.medical_tools import (
    check_red_flags,
    list_available_symptoms,
    lookup_drug_database,
    lookup_medical_knowledge,
)
from backend.app.tools.mcp_client import MCPClient, mcp_client, run_mcp_tool
from backend.app.tools.patient_tools import (
    ask_patient,
    collect_patient_information,
    generate_clinical_summary,
    record_patient_answer,
)
from backend.app.tools.recommendation_tools import (
    get_care_level_guidance,
    recommend_intermediate_care,
)

ALL_TOOLS = [
    collect_patient_information,
    ask_patient,
    record_patient_answer,
    generate_clinical_summary,
    recommend_intermediate_care,
    get_care_level_guidance,
    lookup_medical_knowledge,
    lookup_drug_database,
    list_available_symptoms,
    check_red_flags,
]

__all__ = [
    "ALL_TOOLS",
    "MCPClient",
    "mcp_client",
    "run_mcp_tool",
    "collect_patient_information",
    "ask_patient",
    "record_patient_answer",
    "generate_clinical_summary",
    "recommend_intermediate_care",
    "get_care_level_guidance",
    "lookup_medical_knowledge",
    "lookup_drug_database",
    "list_available_symptoms",
    "check_red_flags",
]
