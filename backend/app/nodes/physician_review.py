"""Physician Review Agent - Human-in-the-Loop workflow pause."""

from datetime import datetime

from langchain_core.messages import AIMessage

from backend.app.middleware.logging_middleware import get_logger, log_node_transition
from backend.app.state import MedicalState

logger = get_logger("nodes.physician_review")


def physician_review_node(state: MedicalState) -> dict:
    """
    Physician Review node - Human-in-the-Loop interruption point.

    The workflow PAUSES here until a physician submits review via API.

    Physician can:
    - Review Clinical Summary
    - Modify Intermediate Recommendation
    - Add treatment notes
    - Approve or reject the report
    """
    thread_id = state.get("thread_id", "unknown")
    physician_review = state.get("physician_review", {})
    clinical_summary = state.get("clinical_summary", "")
    intermediate_recommendation = state.get("intermediate_recommendation", "")

    logger.info(
        "physician_review_node",
        thread_id=thread_id,
        approved=physician_review.get("approved"),
    )

    # Check if physician has submitted review
    if physician_review.get("reviewed_at"):
        if physician_review.get("approved"):
            log_node_transition(logger, "physician_review", "report_agent", thread_id)
            return {
                "consultation_status": "generating_report",
                "physician_treatment": physician_review.get("physician_treatment", ""),
                "intermediate_recommendation": (
                    physician_review.get("modified_recommendation")
                    or intermediate_recommendation
                ),
                "next": "report_agent",
                "messages": [
                    AIMessage(content="Physician approved. Proceeding to report generation.")
                ],
            }
        else:
            log_node_transition(logger, "physician_review", "end", thread_id)
            return {
                "consultation_status": "rejected",
                "next": "end",
                "messages": [
                    AIMessage(content="Physician rejected the consultation. Workflow terminated.")
                ],
            }

    # Workflow paused - waiting for human input
    log_node_transition(logger, "physician_review", "interrupt", thread_id)
    return {
        "consultation_status": "awaiting_physician_review",
        "next": "physician_review",
        "messages": [
            AIMessage(
                content=(
                    "Workflow paused for physician review.\n"
                    f"Clinical Summary: {clinical_summary[:200]}...\n"
                    "Awaiting physician approval via API."
                )
            )
        ],
    }


def apply_physician_review(
    state: MedicalState,
    approved: bool,
    modified_recommendation: str = "",
    physician_treatment: str = "",
    physician_notes: str = "",
    reviewer_id: str = None,
) -> dict:
    """
    Apply physician review data to state (called from API layer).

    Args:
        state: Current workflow state
        approved: Whether physician approved
        modified_recommendation: Modified recommendation if any
        physician_treatment: Treatment notes from physician
        physician_notes: Additional physician notes
        reviewer_id: Reviewing physician identifier

    Returns:
        State updates dictionary
    """
    review_data = {
        "approved": approved,
        "modified_recommendation": modified_recommendation,
        "physician_notes": physician_notes,
        "reviewed_at": datetime.utcnow().isoformat(),
        "reviewer_id": reviewer_id,
    }

    return {
        "physician_review": review_data,
        "physician_treatment": physician_treatment,
    }


def route_from_physician_review(state: MedicalState) -> str:
    """Conditional edge routing from physician review."""
    status = state.get("consultation_status", "")
    physician_review = state.get("physician_review", {})

    if status == "generating_report" and physician_review.get("approved"):
        return "report_agent"
    if status == "rejected":
        return "__end__"
    if not physician_review.get("reviewed_at"):
        return "__end__"  # Interrupt - wait for human input
    return "report_agent"
