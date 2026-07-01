"""Patient interaction tools for the Diagnostic Agent."""

from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger, log_tool_call

logger = get_logger("tools.patient")

# Predefined question templates - customized based on chief complaint
BASE_QUESTIONS = [
    "What symptoms are you experiencing?",
    "When did the symptoms begin?",
    "Do you have fever?",
    "Do you have any chronic diseases?",
    "Are you currently taking any medication?",
]

RESPIRATORY_QUESTIONS = [
    "What respiratory symptoms are you experiencing (cough, shortness of breath, etc.)?",
    "When did these symptoms begin?",
    "Do you have fever or chills?",
    "Do you have asthma, COPD, or other chronic respiratory conditions?",
    "Are you currently taking any medication, including inhalers?",
]


def _get_questions_for_complaint(chief_complaint: str) -> List[str]:
    """Select question set based on chief complaint keywords."""
    complaint_lower = chief_complaint.lower()
    respiratory_keywords = ["cough", "breath", "respiratory", "lung", "throat", "cold", "flu"]
    if any(kw in complaint_lower for kw in respiratory_keywords):
        return RESPIRATORY_QUESTIONS
    return BASE_QUESTIONS


@tool
def collect_patient_information(
    name: str,
    age: int,
    gender: str,
    medical_history: str = "",
    chief_complaint: str = "",
) -> Dict[str, Any]:
    """
    Collect and validate patient demographic and clinical intake information.

    Args:
        name: Patient full name
        age: Patient age in years
        gender: Patient gender
        medical_history: Past medical history
        chief_complaint: Primary reason for consultation

    Returns:
        Validated patient information dictionary
    """
    log_tool_call(logger, "collect_patient_information", name=name, age=age)
    settings = get_settings()

    patient_info = {
        "name": name.strip(),
        "age": age,
        "gender": gender.strip(),
        "medical_history": medical_history.strip() or "None reported",
        "chief_complaint": chief_complaint.strip() or "General consultation",
    }

    return {
        "patient_information": patient_info,
        "status": "collected",
        "disclaimer": settings.medical_disclaimer,
    }


@tool
def ask_patient(question_number: int, chief_complaint: str = "") -> Dict[str, Any]:
    """
    Generate the next sequential diagnostic question for the patient.

    Asks exactly one question at a time. Maximum 5 questions total.

    Args:
        question_number: Current question number (1-5)
        chief_complaint: Chief complaint for question customization

    Returns:
        Question text and metadata
    """
    log_tool_call(logger, "ask_patient", question_number=question_number)
    settings = get_settings()
    max_questions = settings.max_questions

    if question_number < 1 or question_number > max_questions:
        return {
            "error": f"Question number must be between 1 and {max_questions}",
            "question": None,
            "question_number": question_number,
        }

    questions = _get_questions_for_complaint(chief_complaint)
    question_text = questions[question_number - 1]

    return {
        "question": question_text,
        "question_number": question_number,
        "total_questions": max_questions,
        "progress": f"{question_number}/{max_questions}",
        "awaiting_answer": True,
    }


@tool
def record_patient_answer(
    question_number: int,
    question: str,
    answer: str,
) -> Dict[str, Any]:
    """
    Record a patient's answer to a diagnostic question.

    Args:
        question_number: Question sequence number
        question: The question that was asked
        answer: Patient's response

    Returns:
        Recorded answer with metadata
    """
    log_tool_call(logger, "record_patient_answer", question_number=question_number)

    return {
        "patient_answer": {
            "question_number": question_number,
            "question": question,
            "answer": answer.strip(),
        },
        "recorded": True,
    }


@tool
def generate_clinical_summary(
    patient_info: Dict[str, Any],
    patient_answers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate a Clinical Summary from patient data and answers.

    This produces an educational orientation summary, NOT a medical diagnosis.

    Args:
        patient_info: Patient demographic information
        patient_answers: List of Q&A pairs

    Returns:
        Clinical summary and possible observations
    """
    log_tool_call(logger, "generate_clinical_summary")

    settings = get_settings()
    name = patient_info.get("name", "Patient")
    age = patient_info.get("age", "unknown")
    chief_complaint = patient_info.get("chief_complaint", "unspecified symptoms")

    answers_text = "\n".join(
        f"Q{a.get('question_number', '?')}: {a.get('question', '')}\nA: {a.get('answer', '')}"
        for a in patient_answers
    )

    # Rule-based summary generation (works without LLM)
    symptoms = next(
        (a["answer"] for a in patient_answers if a.get("question_number") == 1),
        "unspecified symptoms",
    )
    onset = next(
        (a["answer"] for a in patient_answers if a.get("question_number") == 2),
        "unknown onset",
    )
    fever = next(
        (a["answer"] for a in patient_answers if a.get("question_number") == 3),
        "not specified",
    )
    chronic = next(
        (a["answer"] for a in patient_answers if a.get("question_number") == 4),
        "not specified",
    )
    medications = next(
        (a["answer"] for a in patient_answers if a.get("question_number") == 5),
        "not specified",
    )

    clinical_summary = (
        f"Clinical Summary for {name} (age {age}):\n\n"
        f"The patient presents with chief complaint: {chief_complaint}.\n"
        f"Reported symptoms include: {symptoms}.\n"
        f"Symptom onset: {onset}.\n"
        f"Fever status: {fever}.\n"
        f"Chronic conditions: {chronic}.\n"
        f"Current medications: {medications}.\n\n"
        f"This summary represents a preliminary clinical orientation based on "
        f"self-reported information and does NOT constitute a medical diagnosis."
    )

    possible_observations = _generate_observations(patient_answers, chief_complaint)

    return {
        "clinical_summary": clinical_summary,
        "possible_observations": possible_observations,
        "disclaimer": settings.medical_disclaimer,
        "raw_answers": answers_text,
    }


def _generate_observations(
    patient_answers: List[Dict[str, Any]],
    chief_complaint: str,
) -> List[str]:
    """Generate possible observations based on answers (NOT diagnoses)."""
    observations = []

    for answer in patient_answers:
        ans_lower = answer.get("answer", "").lower()
        q_num = answer.get("question_number", 0)

        if q_num == 3 and any(w in ans_lower for w in ["yes", "high", "fever", "38", "39", "40"]):
            observations.append("Elevated body temperature reported - warrants monitoring")
        if q_num == 1 and any(w in ans_lower for w in ["cough", "breath", "chest"]):
            observations.append("Respiratory symptoms reported")
        if q_num == 1 and any(w in ans_lower for w in ["severe", "intense", " unbearable"]):
            observations.append("Patient reports significant symptom intensity")
        if q_num == 2 and any(w in ans_lower for w in ["sudden", "abrupt", "acute"]):
            observations.append("Acute onset of symptoms noted")

    if not observations:
        observations.append("Self-reported symptoms require professional evaluation")

    observations.append(
        "Further clinical assessment by a qualified healthcare professional is recommended"
    )
    return observations
