"""Pytest configuration and fixtures for MediGraph AI tests."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use temp database for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LANGGRAPH_CHECKPOINT_DIR"] = tempfile.mkdtemp()
os.environ["OPENAI_API_KEY"] = "test-key"


@pytest.fixture
def sample_patient():
    """Sample patient data for tests."""
    return {
        "name": "John Doe",
        "age": 35,
        "gender": "male",
        "medical_history": "None",
        "chief_complaint": "Persistent cough for 3 days",
    }


@pytest.fixture
def respiratory_patient():
    """Patient with respiratory symptoms (Case 1)."""
    return {
        "name": "Alice Smith",
        "age": 28,
        "gender": "female",
        "medical_history": "Asthma",
        "chief_complaint": "Cough and mild fever",
    }


@pytest.fixture
def red_flag_patient():
    """Patient with red flag symptoms (Case 2)."""
    return {
        "name": "Bob Wilson",
        "age": 55,
        "gender": "male",
        "medical_history": "Hypertension",
        "chief_complaint": "Severe chest pain and difficulty breathing",
    }


@pytest.fixture
def benign_patient():
    """Patient with benign symptoms (Case 3)."""
    return {
        "name": "Carol Lee",
        "age": 22,
        "gender": "female",
        "medical_history": "None",
        "chief_complaint": "Mild headache after studying",
    }


@pytest.fixture
def respiratory_answers():
    """Answers for respiratory syndrome case."""
    return [
        {"question_number": 1, "question": "What symptoms?", "answer": "Dry cough and sore throat"},
        {"question_number": 2, "question": "When began?", "answer": "3 days ago"},
        {"question_number": 3, "question": "Fever?", "answer": "Mild fever, around 37.8°C"},
        {"question_number": 4, "question": "Chronic diseases?", "answer": "Asthma, well controlled"},
        {"question_number": 5, "question": "Medications?", "answer": "Salbutamol inhaler as needed"},
    ]
