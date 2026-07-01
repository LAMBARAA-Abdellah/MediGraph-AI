"""FastAPI application and REST API endpoints."""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from backend.app import __version__
from backend.app.config import get_settings
from backend.app.middleware import RequestLoggingMiddleware
from backend.app.middleware.logging_middleware import setup_logging, get_logger
from backend.app.schemas import (
    AnswerSubmitRequest,
    ConsultationResumeRequest,
    ConsultationStartRequest,
    ConsultationStatusResponse,
    ErrorResponse,
    HealthResponse,
    MetricsResponse,
    PhysicianReviewRequest,
    ReportResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from backend.app.services.consultation_service import consultation_service

# Metrics
REQUEST_COUNT = Counter("medigraph_requests_total", "Total API requests", ["endpoint", "method"])

setup_logging()
logger = get_logger("api")
settings = get_settings()

app = FastAPI(
    title="MediGraph AI",
    description=(
        "Intelligent Multi-Agent Clinical Orientation System. "
        "Educational project only - does NOT provide medical diagnosis."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    consultation_service.initialize_database()
    logger.info("application_started", version=__version__)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    REQUEST_COUNT.labels(endpoint="/health", method="GET").inc()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=__version__,
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/metrics", response_model=MetricsResponse, tags=["System"])
async def get_metrics():
    """Application business metrics."""
    metrics_data = consultation_service.get_metrics()
    return MetricsResponse(**metrics_data)


@app.post(
    "/sessions/start",
    response_model=SessionStartResponse,
    tags=["Sessions"],
    responses={400: {"model": ErrorResponse}},
)
async def start_session(request: SessionStartRequest):
    """
    Start a new patient session.

    Creates patient record and initializes LangGraph workflow thread.
    """
    REQUEST_COUNT.labels(endpoint="/sessions/start", method="POST").inc()
    try:
        result = consultation_service.start_session(request.patient)
        return SessionStartResponse(**result)
    except Exception as e:
        logger.error("start_session_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/consultation/start",
    response_model=ConsultationStatusResponse,
    tags=["Consultation"],
)
async def start_consultation(request: ConsultationStartRequest):
    """Start the diagnostic questionnaire for a consultation."""
    REQUEST_COUNT.labels(endpoint="/consultation/start", method="POST").inc()
    try:
        result = consultation_service.start_consultation(request.thread_id)
        return ConsultationStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("start_consultation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/consultation/answer",
    response_model=ConsultationStatusResponse,
    tags=["Consultation"],
)
async def submit_answer(request: AnswerSubmitRequest):
    """Submit patient answer to current diagnostic question."""
    REQUEST_COUNT.labels(endpoint="/consultation/answer", method="POST").inc()
    try:
        result = consultation_service.submit_answer(request.thread_id, request.answer)
        return ConsultationStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("submit_answer_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/consultation/physician-review",
    response_model=ConsultationStatusResponse,
    tags=["Consultation"],
)
async def submit_physician_review(request: PhysicianReviewRequest):
    """
    Submit physician review (Human-in-the-Loop).

    Approves or rejects consultation and optionally modifies recommendations.
    """
    REQUEST_COUNT.labels(endpoint="/consultation/physician-review", method="POST").inc()
    try:
        result = consultation_service.submit_physician_review(
            thread_id=request.thread_id,
            approved=request.approved,
            modified_recommendation=request.modified_recommendation,
            physician_treatment=request.physician_treatment,
            physician_notes=request.physician_notes,
            reviewer_id=request.reviewer_id,
        )
        return ConsultationStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("physician_review_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/consultation/resume",
    response_model=ConsultationStatusResponse,
    tags=["Consultation"],
)
async def resume_consultation(request: ConsultationResumeRequest):
    """Resume an interrupted consultation workflow."""
    REQUEST_COUNT.labels(endpoint="/consultation/resume", method="POST").inc()
    try:
        result = consultation_service.resume_consultation(request.thread_id)
        return ConsultationStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("resume_consultation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/consultation/{thread_id}",
    response_model=ConsultationStatusResponse,
    tags=["Consultation"],
)
async def get_consultation(thread_id: str):
    """Get current consultation state."""
    REQUEST_COUNT.labels(endpoint="/consultation/{thread_id}", method="GET").inc()
    state = consultation_service.get_consultation_state(thread_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Consultation not found: {thread_id}")
    formatted = consultation_service._format_state_response(thread_id, state)
    return ConsultationStatusResponse(**formatted)


@app.get(
    "/consultation/{thread_id}/report",
    response_model=ReportResponse,
    tags=["Consultation"],
)
async def get_report(thread_id: str):
    """Get generated report for a completed consultation."""
    REQUEST_COUNT.labels(endpoint="/consultation/{thread_id}/report", method="GET").inc()
    report = consultation_service.get_report(thread_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or consultation incomplete")
    return ReportResponse(**report)


@app.get("/consultation/{thread_id}/report/pdf", tags=["Consultation"])
async def download_pdf_report(thread_id: str):
    """Download PDF report."""
    report = consultation_service.get_report(thread_id)
    if not report or not report.get("pdf_path"):
        raise HTTPException(status_code=404, detail="PDF report not available")
    return FileResponse(
        report["pdf_path"],
        media_type="application/pdf",
        filename=f"medigraph_report_{thread_id}.pdf",
    )
