"""Supervisor Agent - orchestrates workflow routing and error handling."""

from typing import Literal

from langchain_core.messages import AIMessage

from backend.app.middleware.logging_middleware import get_logger, log_node_transition
from backend.app.state import MedicalState

logger = get_logger("nodes.supervisor")


def supervisor_node(state: MedicalState) -> dict:
    """
    Supervisor Agent node - decides next workflow step.

    Responsibilities:
    - Workflow orchestration
    - Decision making and node routing
    - Error handling
    - Graph transitions
    """
    thread_id = state.get("thread_id", "unknown")
    status = state.get("consultation_status", "initialized")
    question_count = state.get("question_count", 0)
    patient_info = state.get("patient_information", {})
    clinical_summary = state.get("clinical_summary", "")
    physician_review = state.get("physician_review", {})
    error_message = state.get("error_message", "")

    logger.info(
        "supervisor_evaluating",
        thread_id=thread_id,
        status=status,
        question_count=question_count,
    )

    # Error handling
    if error_message:
        log_node_transition(logger, "supervisor", "end", thread_id)
        return {
            "next": "end",
            "consultation_status": "error",
            "messages": [AIMessage(content=f"Workflow error: {error_message}")],
        }

    # Route based on consultation status
    next_node = _determine_next_node(
        status=status,
        question_count=question_count,
        patient_info=patient_info,
        clinical_summary=clinical_summary,
        physician_review=physician_review,
    )

    log_node_transition(logger, "supervisor", next_node, thread_id)

    return {
        "next": next_node,
        "messages": [
            AIMessage(content=f"Supervisor routing to: {next_node} (status: {status})")
        ],
    }


def _determine_next_node(
    status: str,
    question_count: int,
    patient_info: dict,
    clinical_summary: str,
    physician_review: dict,
) -> Literal["diagnostic_agent", "physician_review", "report_agent", "end"]:
    """Determine the next node based on current workflow state."""

    if status == "completed":
        return "end"

    if status == "rejected":
        return "end"

    if status == "generating_report":
        return "report_agent"

    if status == "awaiting_physician_review":
        if physician_review.get("approved") is True:
            return "report_agent"
        if physician_review.get("approved") is False and physician_review.get("reviewed_at"):
            return "end"
        return "physician_review"

    if status in ("questionnaire_in_progress", "collecting_information", "initialized"):
        if not patient_info:
            return "diagnostic_agent"
        if question_count < 5:
            return "diagnostic_agent"
        if question_count >= 5 and not clinical_summary:
            return "diagnostic_agent"
        if clinical_summary and not physician_review:
            return "physician_review"
        if clinical_summary and physician_review.get("approved"):
            return "report_agent"

    # Default: continue diagnostic
    return "diagnostic_agent"


def route_from_supervisor(state: MedicalState) -> str:
    """Conditional edge function for routing from supervisor."""
    next_node = state.get("next", "diagnostic_agent")
    if next_node == "end":
        return "__end__"
    return next_node
