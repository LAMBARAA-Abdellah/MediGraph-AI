"""Shared LangGraph state definition for MediGraph AI clinical workflow."""

from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from langgraph.graph.message import add_messages


ConsultationStatus = Literal[
    "initialized",
    "collecting_information",
    "questionnaire_in_progress",
    "awaiting_physician_review",
    "generating_report",
    "completed",
    "rejected",
    "error",
]

NextNode = Literal[
    "supervisor",
    "diagnostic_agent",
    "physician_review",
    "report_agent",
    "end",
]


class PatientInformation(TypedDict, total=False):
    """Patient demographic and clinical intake data."""

    name: str
    age: int
    gender: str
    medical_history: str
    chief_complaint: str


class PatientAnswer(TypedDict, total=False):
    """Single question-answer pair from the diagnostic questionnaire."""

    question_number: int
    question: str
    answer: str


class PhysicianReviewData(TypedDict, total=False):
    """Physician human-in-the-loop review data."""

    approved: bool
    modified_recommendation: str
    physician_notes: str
    reviewed_at: str
    reviewer_id: Optional[str]


class FinalReportData(TypedDict, total=False):
    """Structured final report output."""

    json_report: Dict[str, Any]
    markdown_report: str
    html_report: str
    pdf_path: str
    generated_at: str


class MedicalState(TypedDict, total=False):
    """
    Shared state for the MediGraph AI LangGraph workflow.

    All agents read from and write to this state. Uses MessagesState
    pattern via add_messages reducer for conversation history.
    """

    # LangGraph MessagesState pattern
    messages: Annotated[list, add_messages]

    # Workflow routing
    next: NextNode

    # Patient data
    patient_information: PatientInformation
    question_count: int
    patient_answers: List[PatientAnswer]
    current_question: str

    # Clinical outputs (orientation only, NOT diagnosis)
    clinical_summary: str
    intermediate_recommendation: str
    possible_observations: List[str]

    # Physician review (human-in-the-loop)
    physician_review: PhysicianReviewData
    physician_treatment: str

    # Final report
    final_report: FinalReportData

    # Workflow status
    consultation_status: ConsultationStatus
    thread_id: str
    error_message: str

    # Internal workflow fields
    _pending_answer: str
