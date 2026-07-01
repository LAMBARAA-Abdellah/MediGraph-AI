"""Diagnostic Agent - asks 5 questions and generates clinical orientation."""

from langchain_core.messages import AIMessage

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger, log_node_transition
from backend.app.state import MedicalState
from backend.app.tools.patient_tools import (
    ask_patient,
    generate_clinical_summary,
    record_patient_answer,
)
from backend.app.tools.recommendation_tools import recommend_intermediate_care

logger = get_logger("nodes.diagnostic_agent")


def diagnostic_agent_node(state: MedicalState) -> dict:
    """
    Diagnostic Agent node - manages questionnaire and clinical orientation.

    Responsibilities:
    - Ask exactly 5 sequential questions via tools
    - Collect and store patient answers
    - Generate Clinical Summary (NOT diagnosis)
    - Generate Intermediate Recommendation
    - List possible observations
    """
    settings = get_settings()
    thread_id = state.get("thread_id", "unknown")
    question_count = state.get("question_count", 0)
    patient_info = state.get("patient_information", {})
    patient_answers = list(state.get("patient_answers", []))
    current_question = state.get("current_question", "")
    pending_answer = state.get("_pending_answer", "")

    logger.info(
        "diagnostic_agent_active",
        thread_id=thread_id,
        question_count=question_count,
    )

    updates: dict = {}

    # Phase 1: Record pending answer if provided
    if pending_answer and current_question and question_count > 0:
        answer_record = record_patient_answer.invoke({
            "question_number": question_count,
            "question": current_question,
            "answer": pending_answer,
        })
        patient_answers.append(answer_record["patient_answer"])
        updates["patient_answers"] = patient_answers
        updates["_pending_answer"] = ""
        logger.info("answer_recorded", question_number=question_count)

    # Phase 2: Ask next question if under limit
    current_count = len(patient_answers)
    if current_count < settings.max_questions:
        next_q_num = current_count + 1
        chief_complaint = patient_info.get("chief_complaint", "")
        question_result = ask_patient.invoke({
            "question_number": next_q_num,
            "chief_complaint": chief_complaint,
        })

        updates.update({
            "question_count": next_q_num,
            "current_question": question_result["question"],
            "consultation_status": "questionnaire_in_progress",
            "next": "supervisor",
            "messages": [
                AIMessage(
                    content=f"Question {next_q_num}/{settings.max_questions}: {question_result['question']}"
                )
            ],
        })

        log_node_transition(logger, "diagnostic_agent", "supervisor", thread_id)
        return updates

    # Phase 3: All questions answered - generate summary and recommendation
    if current_count >= settings.max_questions and not state.get("clinical_summary"):
        summary_result = generate_clinical_summary.invoke({
            "patient_info": patient_info,
            "patient_answers": patient_answers,
        })

        recommendation_result = recommend_intermediate_care.invoke({
            "clinical_summary": summary_result["clinical_summary"],
            "possible_observations": summary_result["possible_observations"],
        })

        updates.update({
            "clinical_summary": summary_result["clinical_summary"],
            "possible_observations": summary_result["possible_observations"],
            "intermediate_recommendation": recommendation_result["intermediate_recommendation"],
            "consultation_status": "awaiting_physician_review",
            "next": "physician_review",
            "messages": [
                AIMessage(content="Clinical Summary and Intermediate Recommendation generated. Awaiting physician review.")
            ],
        })

        log_node_transition(logger, "diagnostic_agent", "physician_review", thread_id)
        return updates

    # Already processed
    updates["next"] = "supervisor"
    return updates


def route_from_diagnostic(state: MedicalState) -> str:
    """Conditional edge routing from diagnostic agent."""
    next_node = state.get("next", "supervisor")
    status = state.get("consultation_status", "")

    if status == "awaiting_physician_review":
        return "physician_review"
    if next_node == "supervisor":
        return "supervisor"
    return "supervisor"
