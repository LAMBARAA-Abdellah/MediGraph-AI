"""SQLAlchemy ORM models for MediGraph AI persistence layer."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from backend.app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Patient(Base):
    """Patient demographic and medical history record."""

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    medical_history = Column(Text, default="")
    chief_complaint = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("Consultation", back_populates="patient")


class Consultation(Base):
    """Clinical consultation session linked to LangGraph thread."""

    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(255), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    status = Column(String(50), default="initialized")
    question_count = Column(Integer, default=0)
    clinical_summary = Column(Text, default="")
    intermediate_recommendation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="consultations")
    questions = relationship("Question", back_populates="consultation", cascade="all, delete-orphan")
    physician_review = relationship(
        "PhysicianReview", back_populates="consultation", uselist=False, cascade="all, delete-orphan"
    )
    report = relationship(
        "Report", back_populates="consultation", uselist=False, cascade="all, delete-orphan"
    )


class Question(Base):
    """Diagnostic questionnaire question."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class Answer(Base):
    """Patient answer to a diagnostic question."""

    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="answer")


class PhysicianReview(Base):
    """Human-in-the-loop physician review record."""

    __tablename__ = "physician_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    approved = Column(Boolean, default=False)
    modified_recommendation = Column(Text, default="")
    physician_treatment = Column(Text, default="")
    physician_notes = Column(Text, default="")
    reviewer_id = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="physician_review")


class Report(Base):
    """Generated clinical orientation report."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    json_report = Column(Text, default="")
    markdown_report = Column(Text, default="")
    html_report = Column(Text, default="")
    pdf_path = Column(String(500), default="")
    disclaimer = Column(Text, default="This system does not replace a professional medical consultation.")
    generated_at = Column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="report")


def get_engine():
    """Create SQLAlchemy engine from settings."""
    settings = get_settings()
    connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
    return create_engine(settings.database_url, connect_args=connect_args)


def get_session_factory():
    """Return a session factory bound to the engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
