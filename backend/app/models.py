"""SQLAlchemy ORM models - re-exported from database module for clean architecture."""

from backend.app.database import (
    Answer,
    Base,
    Consultation,
    Patient,
    PhysicianReview,
    Question,
    Report,
)

__all__ = [
    "Base",
    "Patient",
    "Consultation",
    "Question",
    "Answer",
    "PhysicianReview",
    "Report",
]
