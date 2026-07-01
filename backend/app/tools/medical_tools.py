"""Medical knowledge tools - educational reference only."""

from typing import Any, Dict, List

from langchain_core.tools import tool

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger, log_tool_call

logger = get_logger("tools.medical")

# Demo medical knowledge base (educational purposes only)
MEDICAL_KNOWLEDGE = {
    "fever": {
        "description": "Elevated body temperature above normal range (typically >38°C/100.4°F)",
        "general_guidance": "Monitor temperature, stay hydrated, rest. Seek care if persistent or high.",
        "red_flags": ["Temperature above 39.5°C", "Fever lasting more than 3 days", "Confusion"],
    },
    "cough": {
        "description": "Reflex action to clear airways",
        "general_guidance": "Rest, hydration, honey for soothing (adults). Monitor duration.",
        "red_flags": ["Blood in sputum", "Severe breathing difficulty", "Cough lasting >3 weeks"],
    },
    "headache": {
        "description": "Pain in the head or upper neck region",
        "general_guidance": "Rest in quiet environment, hydration, stress reduction.",
        "red_flags": ["Sudden severe headache", "Headache with fever and stiff neck", "Vision changes"],
    },
    "fatigue": {
        "description": "Persistent feeling of tiredness or exhaustion",
        "general_guidance": "Adequate sleep, balanced nutrition, gradual activity resumption.",
        "red_flags": ["Sudden onset severe fatigue", "Accompanied by chest pain or shortness of breath"],
    },
}

DRUG_DATABASE_DEMO = {
    "paracetamol": {
        "generic_name": "Paracetamol (Acetaminophen)",
        "category": "Analgesic/Antipyretic",
        "note": "Reference only - NOT prescribed by this system",
        "general_info": "Common over-the-counter medication for pain and fever",
    },
    "ibuprofen": {
        "generic_name": "Ibuprofen",
        "category": "NSAID",
        "note": "Reference only - NOT prescribed by this system",
        "general_info": "Anti-inflammatory medication - consult pharmacist/physician",
    },
    "amoxicillin": {
        "generic_name": "Amoxicillin",
        "category": "Antibiotic",
        "note": "Prescription only - NOT prescribed by this system",
        "general_info": "Requires physician prescription and proper diagnosis",
    },
}


@tool
def lookup_medical_knowledge(symptom: str) -> Dict[str, Any]:
    """
    Look up educational medical knowledge for a symptom.

    For educational reference only - NOT for diagnosis.

    Args:
        symptom: Symptom keyword to look up

    Returns:
        Educational medical knowledge entry
    """
    log_tool_call(logger, "lookup_medical_knowledge", symptom=symptom)
    settings = get_settings()
    symptom_lower = symptom.lower().strip()

    for key, data in MEDICAL_KNOWLEDGE.items():
        if key in symptom_lower or symptom_lower in key:
            return {
                "symptom": key,
                "knowledge": data,
                "disclaimer": settings.medical_disclaimer,
                "note": "Educational reference only - not medical advice",
            }

    return {
        "symptom": symptom,
        "knowledge": None,
        "message": f"No educational entry found for '{symptom}'",
        "disclaimer": settings.medical_disclaimer,
    }


@tool
def lookup_drug_database(drug_name: str) -> Dict[str, Any]:
    """
    Demo drug database lookup for educational purposes.

    This system NEVER prescribes medication.

    Args:
        drug_name: Drug name to look up

    Returns:
        Demo drug information
    """
    log_tool_call(logger, "lookup_drug_database", drug_name=drug_name)
    settings = get_settings()
    drug_lower = drug_name.lower().strip()

    for key, data in DRUG_DATABASE_DEMO.items():
        if key in drug_lower or drug_lower in key:
            return {
                "drug": key,
                "information": data,
                "disclaimer": settings.medical_disclaimer,
                "warning": "This system does NOT prescribe medication",
            }

    return {
        "drug": drug_name,
        "information": None,
        "message": f"No demo entry found for '{drug_name}'",
        "disclaimer": settings.medical_disclaimer,
    }


@tool
def list_available_symptoms() -> List[str]:
    """List symptoms available in the demo medical knowledge base."""
    log_tool_call(logger, "list_available_symptoms")
    return list(MEDICAL_KNOWLEDGE.keys())


@tool
def check_red_flags(symptoms: List[str]) -> Dict[str, Any]:
    """
    Check symptoms against known red flag indicators.

    Args:
        symptoms: List of symptom keywords

    Returns:
        Red flag assessment (educational orientation)
    """
    log_tool_call(logger, "check_red_flags", symptoms=symptoms)
    settings = get_settings()
    detected_flags = []

    for symptom in symptoms:
        symptom_lower = symptom.lower()
        for key, data in MEDICAL_KNOWLEDGE.items():
            if key in symptom_lower:
                detected_flags.extend(data.get("red_flags", []))

    return {
        "red_flags_detected": detected_flags,
        "requires_urgent_care": len(detected_flags) > 0,
        "recommendation": (
            "Seek immediate medical evaluation" if detected_flags
            else "Schedule routine consultation"
        ),
        "disclaimer": settings.medical_disclaimer,
    }
