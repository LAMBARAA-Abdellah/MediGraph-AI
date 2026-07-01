# API Documentation

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

## Endpoints

### GET /health

Health check.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "MediGraph AI",
  "version": "1.0.0",
  "timestamp": "2026-07-01T12:00:00"
}
```

### POST /sessions/start

Start a new patient session.

**Request:**
```json
{
  "patient": {
    "name": "John Doe",
    "age": 35,
    "gender": "male",
    "medical_history": "None",
    "chief_complaint": "Persistent cough"
  }
}
```

**Response:**
```json
{
  "thread_id": "uuid",
  "patient_id": 1,
  "consultation_id": 1,
  "status": "collecting_information",
  "message": "Session started."
}
```

### POST /consultation/start

Start diagnostic questionnaire.

**Request:** `{ "thread_id": "uuid" }`

### POST /consultation/answer

Submit patient answer.

**Request:** `{ "thread_id": "uuid", "answer": "3 days ago" }`

### POST /consultation/physician-review

Submit physician review (Human-in-the-Loop).

**Request:**
```json
{
  "thread_id": "uuid",
  "approved": true,
  "modified_recommendation": "",
  "physician_treatment": "Rest and fluids",
  "physician_notes": "Follow up in 5 days",
  "reviewer_id": "DR-001"
}
```

### POST /consultation/resume

Resume interrupted workflow.

### GET /consultation/{thread_id}

Get current consultation state.

### GET /consultation/{thread_id}/report

Get generated report (JSON, Markdown, HTML, PDF path).

### GET /api/metrics

Business metrics (total, completed, pending consultations).

*All responses include the disclaimer: This system does not replace a professional medical consultation.*
