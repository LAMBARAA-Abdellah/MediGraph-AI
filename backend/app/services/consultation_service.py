"""Business logic services for MediGraph AI."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage

from backend.app.config import get_settings
from backend.app.database import Consultation, Patient, PhysicianReview, Question, Answer, Report, get_session_factory, init_db
from backend.app.graph import compile_graph
from backend.app.memory.session_memory import session_memory
from backend.app.middleware.logging_middleware import get_logger
from backend.app.nodes.physician_review import apply_physician_review
from backend.app.schemas import PatientCreate
from backend.app.tools.patient_tools import collect_patient_information

logger = get_logger("services.consultation")


class ConsultationService:
    """Service layer for consultation workflow management."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._graph = None
        self._session_factory = get_session_factory()

    @property
    def graph(self):
        """Lazy-load compiled graph."""
        if self._graph is None:
            self._graph = compile_graph()
        return self._graph

    def initialize_database(self) -> None:
        """Initialize database tables."""
        init_db()
        logger.info("database_initialized")

    def start_session(self, patient_data: PatientCreate) -> Dict[str, Any]:
        """
        Start a new consultation session.

        Creates patient record, consultation, and LangGraph thread.
        """
        thread_id = str(uuid.uuid4())
        session = self._session_factory()

        try:
            # Create patient
            patient = Patient(
                name=patient_data.name,
                age=patient_data.age,
                gender=patient_data.gender,
                medical_history=patient_data.medical_history,
                chief_complaint=patient_data.chief_complaint,
            )
            session.add(patient)
            session.flush()

            # Create consultation
            consultation = Consultation(
                thread_id=thread_id,
                patient_id=patient.id,
                status="initialized",
            )
            session.add(consultation)
            session.commit()

            # Collect patient info via tool
            patient_info_result = collect_patient_information.invoke({
                "name": patient_data.name,
                "age": patient_data.age,
                "gender": patient_data.gender,
                "medical_history": patient_data.medical_history,
                "chief_complaint": patient_data.chief_complaint,
            })

            # Initialize graph state
            initial_state = {
                "messages": [HumanMessage(content=f"New consultation for {patient_data.name}")],
                "thread_id": thread_id,
                "patient_information": patient_info_result["patient_information"],
                "question_count": 0,
                "patient_answers": [],
                "consultation_status": "collecting_information",
                "next": "supervisor",
            }

            config = {"configurable": {"thread_id": thread_id}}
            self.graph.invoke(initial_state, config)

            session_memory.store_session(thread_id, {"patient_id": patient.id, "consultation_id": consultation.id})

            logger.info("session_started", thread_id=thread_id, patient_id=patient.id)

            return {
                "thread_id": thread_id,
                "patient_id": patient.id,
                "consultation_id": consultation.id,
                "status": "collecting_information",
                "message": "Session started. Begin consultation to start questionnaire.",
            }
        finally:
            session.close()

    def start_consultation(self, thread_id: str) -> Dict[str, Any]:
        """Start the diagnostic questionnaire workflow."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.get_consultation_state(thread_id)

        if not current_state:
            raise ValueError(f"Consultation not found: {thread_id}")

        # Invoke graph to start asking questions
        result = self.graph.invoke(
            {"consultation_status": "questionnaire_in_progress", "next": "supervisor"},
            config,
        )

        return self._format_state_response(thread_id, result)

    def submit_answer(self, thread_id: str, answer: str) -> Dict[str, Any]:
        """Submit patient answer to current question."""
        config = {"configurable": {"thread_id": thread_id}}
        current = self.get_consultation_state(thread_id)

        if not current:
            raise ValueError(f"Consultation not found: {thread_id}")

        question_count = current.get("question_count", 0)
        current_question = current.get("current_question", "")

        # Save answer to database
        self._save_answer_to_db(thread_id, question_count, current_question, answer)

        # Update state with pending answer and continue workflow
        update_state = {
            "_pending_answer": answer,
            "question_count": question_count,
            "current_question": current_question,
            "next": "diagnostic_agent",
        }

        result = self.graph.invoke(update_state, config)
        return self._format_state_response(thread_id, result)

    def submit_physician_review(
        self,
        thread_id: str,
        approved: bool,
        modified_recommendation: str = "",
        physician_treatment: str = "",
        physician_notes: str = "",
        reviewer_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit physician review and resume workflow."""
        config = {"configurable": {"thread_id": thread_id}}
        current = self.get_consultation_state(thread_id)

        if not current:
            raise ValueError(f"Consultation not found: {thread_id}")

        review_updates = apply_physician_review(
            current,
            approved=approved,
            modified_recommendation=modified_recommendation,
            physician_treatment=physician_treatment,
            physician_notes=physician_notes,
            reviewer_id=reviewer_id,
        )

        # Save to database
        self._save_physician_review_to_db(
            thread_id, approved, modified_recommendation,
            physician_treatment, physician_notes, reviewer_id,
        )

        # Update state
        self.graph.update_state(config, review_updates)

        if approved:
            # Resume interrupted workflow
            result = self.graph.invoke(None, config)
            return self._format_state_response(thread_id, result)

        return self._format_state_response(thread_id, {**current, **review_updates, "consultation_status": "rejected"})

    def resume_consultation(self, thread_id: str) -> Dict[str, Any]:
        """Resume an interrupted consultation workflow."""
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(None, config)
        return self._format_state_response(thread_id, result)

    def get_consultation_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get current consultation state from graph checkpoint."""
        config = {"configurable": {"thread_id": thread_id}}
        try:
            state_snapshot = self.graph.get_state(config)
            if state_snapshot and state_snapshot.values:
                return dict(state_snapshot.values)
        except Exception as e:
            logger.error("get_state_failed", thread_id=thread_id, error=str(e))
        return None

    def get_report(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get generated report for a consultation."""
        state = self.get_consultation_state(thread_id)
        if not state:
            return None

        final_report = state.get("final_report")
        if not final_report:
            return None

        settings = self.settings
        return {
            "thread_id": thread_id,
            "json_report": final_report.get("json_report", {}),
            "markdown_report": final_report.get("markdown_report", ""),
            "html_report": final_report.get("html_report", ""),
            "pdf_path": final_report.get("pdf_path"),
            "disclaimer": settings.medical_disclaimer,
            "generated_at": final_report.get("generated_at"),
        }

    def get_metrics(self) -> Dict[str, int]:
        """Get application metrics."""
        session = self._session_factory()
        try:
            total = session.query(Consultation).count()
            completed = session.query(Consultation).filter(Consultation.status == "completed").count()
            pending = session.query(Consultation).filter(
                Consultation.status == "awaiting_physician_review"
            ).count()
            return {
                "total_consultations": total,
                "completed_consultations": completed,
                "pending_reviews": pending,
                "active_sessions": total - completed,
            }
        finally:
            session.close()

    def _format_state_response(self, thread_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Format graph state into API response."""
        physician_review = state.get("physician_review", {})
        final_report = state.get("final_report")

        return {
            "thread_id": thread_id,
            "consultation_status": state.get("consultation_status", "unknown"),
            "question_count": state.get("question_count", 0),
            "current_question": state.get("current_question"),
            "patient_information": state.get("patient_information"),
            "patient_answers": state.get("patient_answers", []),
            "clinical_summary": state.get("clinical_summary"),
            "intermediate_recommendation": state.get("intermediate_recommendation"),
            "possible_observations": state.get("possible_observations", []),
            "physician_review": physician_review if physician_review else None,
            "physician_treatment": state.get("physician_treatment"),
            "final_report": final_report,
            "error_message": state.get("error_message"),
        }

    def _save_answer_to_db(self, thread_id: str, q_num: int, question: str, answer: str) -> None:
        """Persist Q&A to database."""
        session = self._session_factory()
        try:
            consultation = session.query(Consultation).filter_by(thread_id=thread_id).first()
            if consultation:
                q = Question(
                    consultation_id=consultation.id,
                    question_number=q_num,
                    question_text=question,
                )
                session.add(q)
                session.flush()
                session.add(Answer(question_id=q.id, answer_text=answer))
                consultation.question_count = q_num
                session.commit()
        finally:
            session.close()

    def _save_physician_review_to_db(
        self, thread_id, approved, modified_rec, treatment, notes, reviewer_id
    ) -> None:
        """Persist physician review to database."""
        session = self._session_factory()
        try:
            consultation = session.query(Consultation).filter_by(thread_id=thread_id).first()
            if consultation:
                review = PhysicianReview(
                    consultation_id=consultation.id,
                    approved=approved,
                    modified_recommendation=modified_rec,
                    physician_treatment=treatment,
                    physician_notes=notes,
                    reviewer_id=reviewer_id,
                )
                session.add(review)
                consultation.status = "generating_report" if approved else "rejected"
                session.commit()
        finally:
            session.close()


# Singleton service
consultation_service = ConsultationService()
