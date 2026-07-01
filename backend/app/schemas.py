"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- Patient Schemas ---


class PatientCreate(BaseModel):
    """Schema for patient registration."""

    name: str = Field(..., min_length=1, max_length=255)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., min_length=1, max_length=50)
    medical_history: str = Field(default="")
    chief_complaint: str = Field(default="")


class PatientResponse(BaseModel):
    """Schema for patient response."""

    id: int
    name: str
    age: int
    gender: str
    medical_history: str
    chief_complaint: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Consultation Schemas ---


class SessionStartRequest(BaseModel):
    """Request to start a new session."""

    patient: PatientCreate


class SessionStartResponse(BaseModel):
    """Response after starting a session."""

    thread_id: str
    patient_id: int
    consultation_id: int
    status: str
    message: str


class ConsultationStartRequest(BaseModel):
    """Request to start consultation workflow."""

    thread_id: str


class AnswerSubmitRequest(BaseModel):
    """Submit answer to current diagnostic question."""

    thread_id: str
    answer: str = Field(..., min_length=1)


class PhysicianReviewRequest(BaseModel):
    """Physician review submission for human-in-the-loop."""

    thread_id: str
    approved: bool
    modified_recommendation: str = Field(default="")
    physician_treatment: str = Field(default="")
    physician_notes: str = Field(default="")
    reviewer_id: Optional[str] = None


class ConsultationResumeRequest(BaseModel):
    """Resume interrupted workflow after physician review."""

    thread_id: str


class PatientAnswerSchema(BaseModel):
    """Single Q&A pair."""

    question_number: int
    question: str
    answer: str


class PhysicianReviewResponse(BaseModel):
    """Physician review data."""

    approved: bool
    modified_recommendation: str = ""
    physician_treatment: str = ""
    physician_notes: str = ""
    reviewed_at: Optional[str] = None


class ConsultationStatusResponse(BaseModel):
    """Full consultation state response."""

    thread_id: str
    consultation_status: str
    question_count: int
    current_question: Optional[str] = None
    patient_information: Optional[Dict[str, Any]] = None
    patient_answers: List[PatientAnswerSchema] = []
    clinical_summary: Optional[str] = None
    intermediate_recommendation: Optional[str] = None
    possible_observations: List[str] = []
    physician_review: Optional[PhysicianReviewResponse] = None
    physician_treatment: Optional[str] = None
    final_report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ReportResponse(BaseModel):
    """Generated report response."""

    thread_id: str
    json_report: Dict[str, Any]
    markdown_report: str
    html_report: str
    pdf_path: Optional[str] = None
    disclaimer: str = "This system does not replace a professional medical consultation."
    generated_at: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    app_name: str
    version: str
    timestamp: str


class MetricsResponse(BaseModel):
    """Application metrics response."""

    total_consultations: int
    completed_consultations: int
    pending_reviews: int
    active_sessions: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    error_code: Optional[str] = None
