"""MediGraph AI workflow tests - Cases 1, 2, and 3."""

import pytest

from backend.app.config import get_settings
from backend.app.tools.patient_tools import (
    ask_patient,
    collect_patient_information,
    generate_clinical_summary,
)
from backend.app.tools.recommendation_tools import recommend_intermediate_care
from backend.app.nodes.supervisor import _determine_next_node


class TestPatientTools:
    """Test patient interaction tools."""

    def test_collect_patient_information(self, sample_patient):
        result = collect_patient_information.invoke(sample_patient)
        assert result["status"] == "collected"
        assert result["patient_information"]["name"] == "John Doe"
        assert "disclaimer" in result

    def test_ask_patient_sequential(self):
        for i in range(1, 6):
            result = ask_patient.invoke({"question_number": i, "chief_complaint": "cough"})
            assert result["question"] is not None
            assert result["question_number"] == i
            assert result["total_questions"] == 5

    def test_ask_patient_invalid_number(self):
        result = ask_patient.invoke({"question_number": 6})
        assert "error" in result

    def test_exactly_five_questions(self):
        settings = get_settings()
        assert settings.max_questions == 5


class TestClinicalSummary:
    """Test clinical summary generation."""

    def test_generate_clinical_summary(self, sample_patient, respiratory_answers):
        result = generate_clinical_summary.invoke({
            "patient_info": sample_patient,
            "patient_answers": respiratory_answers,
        })
        assert "clinical_summary" in result
        assert "possible_observations" in result
        assert "diagnosis" not in result["clinical_summary"].lower() or "NOT" in result["clinical_summary"]
        assert result["disclaimer"]


class TestIntermediateRecommendation:
    """Test intermediate recommendation tool."""

    def test_safe_recommendations(self):
        result = recommend_intermediate_care.invoke({
            "clinical_summary": "Patient reports mild cough for 3 days",
            "possible_observations": ["Respiratory symptoms reported"],
        })
        assert "intermediate_recommendation" in result
        assert result["urgency_level"] == "routine"
        rec_text = result["intermediate_recommendation"].lower()
        assert "rest" in rec_text or "hydration" in rec_text

    def test_red_flag_recommendations(self):
        result = recommend_intermediate_care.invoke({
            "clinical_summary": "Patient reports severe chest pain and difficulty breathing",
            "possible_observations": ["Severe symptoms reported"],
        })
        assert result["has_red_flags"] is True
        assert result["urgency_level"] == "high"

    def test_no_medication_prescription(self):
        result = recommend_intermediate_care.invoke({
            "clinical_summary": "Mild symptoms",
            "possible_observations": [],
        })
        rec_lower = result["intermediate_recommendation"].lower()
        assert "prescribe" not in rec_lower


class TestSupervisorRouting:
    """Test supervisor agent routing logic."""

    def test_route_to_diagnostic_when_no_questions(self):
        next_node = _determine_next_node(
            status="initialized",
            question_count=0,
            patient_info={"name": "Test"},
            clinical_summary="",
            physician_review={},
        )
        assert next_node == "diagnostic_agent"

    def test_route_to_physician_review(self):
        next_node = _determine_next_node(
            status="awaiting_physician_review",
            question_count=5,
            patient_info={"name": "Test"},
            clinical_summary="Summary here",
            physician_review={},
        )
        assert next_node == "physician_review"

    def test_route_to_report_after_approval(self):
        next_node = _determine_next_node(
            status="awaiting_physician_review",
            question_count=5,
            patient_info={"name": "Test"},
            clinical_summary="Summary",
            physician_review={"approved": True},
        )
        assert next_node == "report_agent"


class TestCase1RespiratorySyndrome:
    """Case 1: Simple Respiratory Syndrome."""

    def test_respiratory_workflow(self, respiratory_patient, respiratory_answers):
        # Collect info
        info = collect_patient_information.invoke(respiratory_patient)
        assert info["patient_information"]["chief_complaint"]

        # Generate summary
        summary = generate_clinical_summary.invoke({
            "patient_info": info["patient_information"],
            "patient_answers": respiratory_answers,
        })
        assert "cough" in summary["clinical_summary"].lower() or "respiratory" in str(summary).lower()

        # Recommendation
        rec = recommend_intermediate_care.invoke({
            "clinical_summary": summary["clinical_summary"],
            "possible_observations": summary["possible_observations"],
        })
        assert rec["intermediate_recommendation"]
        assert len(respiratory_answers) == 5


class TestCase2RedFlags:
    """Case 2: Red Flags."""

    def test_red_flag_detection(self, red_flag_patient):
        answers = [
            {"question_number": 1, "question": "Symptoms?", "answer": "Severe chest pain and difficulty breathing"},
            {"question_number": 2, "question": "Onset?", "answer": "Sudden, 1 hour ago"},
            {"question_number": 3, "question": "Fever?", "answer": "No fever"},
            {"question_number": 4, "question": "Chronic?", "answer": "Hypertension"},
            {"question_number": 5, "question": "Medications?", "answer": "Lisinopril"},
        ]
        summary = generate_clinical_summary.invoke({
            "patient_info": red_flag_patient,
            "patient_answers": answers,
        })
        rec = recommend_intermediate_care.invoke({
            "clinical_summary": summary["clinical_summary"],
            "possible_observations": summary["possible_observations"],
        })
        assert rec["has_red_flags"] is True
        assert rec["urgency_level"] == "high"


class TestCase3BenignCase:
    """Case 3: Benign Case."""

    def test_benign_workflow(self, benign_patient):
        answers = [
            {"question_number": 1, "question": "Symptoms?", "answer": "Mild headache"},
            {"question_number": 2, "question": "Onset?", "answer": "This morning after studying"},
            {"question_number": 3, "question": "Fever?", "answer": "No"},
            {"question_number": 4, "question": "Chronic?", "answer": "None"},
            {"question_number": 5, "question": "Medications?", "answer": "None"},
        ]
        summary = generate_clinical_summary.invoke({
            "patient_info": benign_patient,
            "patient_answers": answers,
        })
        rec = recommend_intermediate_care.invoke({
            "clinical_summary": summary["clinical_summary"],
            "possible_observations": summary["possible_observations"],
        })
        assert rec["urgency_level"] == "routine"
        assert rec["has_red_flags"] is False


class TestDisclaimer:
    """Verify mandatory disclaimer presence."""

    def test_disclaimer_in_tools(self):
        settings = get_settings()
        assert "does not replace" in settings.medical_disclaimer.lower()

    def test_disclaimer_in_recommendation(self):
        result = recommend_intermediate_care.invoke({
            "clinical_summary": "Test",
            "possible_observations": [],
        })
        assert "does not replace" in result["disclaimer"].lower()
