"""Intermediate recommendation tools - safe orientation only, no prescriptions."""

from typing import Any, Dict, List

from langchain_core.tools import tool

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger, log_tool_call

logger = get_logger("tools.recommendation")

SAFE_RECOMMENDATIONS = [
    "Rest and allow the body time to recover",
    "Maintain adequate hydration by drinking plenty of fluids",
    "Monitor symptoms and note any changes in severity",
    "Schedule a consultation with a qualified healthcare professional",
    "Keep a symptom diary to share with your physician",
]

RED_FLAG_RECOMMENDATIONS = [
    "Seek immediate emergency care if symptoms worsen rapidly",
    "Visit the emergency department if experiencing severe difficulty breathing",
    "Contact emergency services if chest pain or severe symptoms occur",
    "Do not delay professional medical evaluation for worsening symptoms",
]


@tool
def recommend_intermediate_care(
    clinical_summary: str,
    possible_observations: List[str],
) -> Dict[str, Any]:
    """
    Generate safe Intermediate Recommendations based on clinical summary.

    NEVER prescribes medication. Provides orientation guidance only.

    Args:
        clinical_summary: Generated clinical summary text
        possible_observations: List of possible observations

    Returns:
        Intermediate recommendation text and action items
    """
    log_tool_call(logger, "recommend_intermediate_care")
    settings = get_settings()

    has_red_flags = _detect_red_flags(clinical_summary, possible_observations)

    recommendations = list(SAFE_RECOMMENDATIONS)
    if has_red_flags:
        recommendations.extend(RED_FLAG_RECOMMENDATIONS)

    recommendation_text = (
        "Intermediate Recommendation:\n\n"
        + "\n".join(f"• {rec}" for rec in recommendations)
        + f"\n\n{settings.medical_disclaimer}"
    )

    return {
        "intermediate_recommendation": recommendation_text,
        "recommendations": recommendations,
        "has_red_flags": has_red_flags,
        "urgency_level": "high" if has_red_flags else "routine",
        "disclaimer": settings.medical_disclaimer,
    }


def _detect_red_flags(clinical_summary: str, observations: List[str]) -> bool:
    """Detect potential red flag indicators in summary and observations."""
    red_flag_keywords = [
        "severe", "chest pain", "difficulty breathing", "unconscious",
        "bleeding", "emergency", "intense", "worsening rapidly",
        "high fever", "39", "40", "41",
    ]
    combined_text = (clinical_summary + " " + " ".join(observations)).lower()
    return any(keyword in combined_text for keyword in red_flag_keywords)


@tool
def get_care_level_guidance(urgency_level: str = "routine") -> Dict[str, Any]:
    """
    Provide care level guidance based on urgency assessment.

    Args:
        urgency_level: 'routine' or 'high'

    Returns:
        Care level guidance
    """
    log_tool_call(logger, "get_care_level_guidance", urgency_level=urgency_level)
    settings = get_settings()

    if urgency_level == "high":
        guidance = {
            "level": "urgent",
            "action": "Seek prompt medical evaluation",
            "timeline": "Within 24 hours or immediately if symptoms worsen",
            "self_care": ["Rest", "Hydration", "Monitor vital signs if possible"],
        }
    else:
        guidance = {
            "level": "routine",
            "action": "Schedule consultation with healthcare provider",
            "timeline": "Within 3-5 days",
            "self_care": ["Rest", "Hydration", "Observation"],
        }

    guidance["disclaimer"] = settings.medical_disclaimer
    return guidance
