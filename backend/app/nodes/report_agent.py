"""Report Agent - generates structured clinical orientation reports."""

import json
from datetime import datetime
from pathlib import Path

from langchain_core.messages import AIMessage
from jinja2 import Template

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger, log_node_transition
from backend.app.state import MedicalState

logger = get_logger("nodes.report_agent")

REPORT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MediGraph AI - Clinical Orientation Report</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
        h1 { color: #2c5282; border-bottom: 2px solid #2c5282; padding-bottom: 10px; }
        h2 { color: #2d3748; margin-top: 30px; }
        .section { background: #f7fafc; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .disclaimer { background: #fff5f5; border-left: 4px solid #e53e3e; padding: 15px; margin-top: 30px; }
        .qa-pair { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }
        .label { font-weight: bold; color: #4a5568; }
    </style>
</head>
<body>
    <h1>MediGraph AI - Preliminary Clinical Orientation Report</h1>
    <p><em>Generated: {{ generated_at }}</em></p>

    <h2>Patient Information</h2>
    <div class="section">
        <p><span class="label">Name:</span> {{ patient.name }}</p>
        <p><span class="label">Age:</span> {{ patient.age }}</p>
        <p><span class="label">Gender:</span> {{ patient.gender }}</p>
        <p><span class="label">Medical History:</span> {{ patient.medical_history }}</p>
        <p><span class="label">Chief Complaint:</span> {{ patient.chief_complaint }}</p>
    </div>

    <h2>Patient Questionnaire</h2>
    <div class="section">
        {% for qa in answers %}
        <div class="qa-pair">
            <p><span class="label">Q{{ qa.question_number }}:</span> {{ qa.question }}</p>
            <p><span class="label">Answer:</span> {{ qa.answer }}</p>
        </div>
        {% endfor %}
    </div>

    <h2>Clinical Summary</h2>
    <div class="section"><pre>{{ clinical_summary }}</pre></div>

    <h2>Intermediate Recommendation</h2>
    <div class="section"><pre>{{ intermediate_recommendation }}</pre></div>

    {% if physician_review %}
    <h2>Physician Review</h2>
    <div class="section">
        <p><span class="label">Approved:</span> {{ physician_review.approved }}</p>
        <p><span class="label">Notes:</span> {{ physician_review.physician_notes }}</p>
    </div>
    {% endif %}

    {% if physician_treatment %}
    <h2>Physician Treatment</h2>
    <div class="section"><pre>{{ physician_treatment }}</pre></div>
    {% endif %}

    <h2>Final Notes</h2>
    <div class="section">
        <p>This report represents a preliminary clinical orientation for educational purposes.</p>
        <p>Possible observations: {{ observations }}</p>
    </div>

    <div class="disclaimer">
        <strong>Disclaimer:</strong> {{ disclaimer }}
    </div>
</body>
</html>
"""


def report_agent_node(state: MedicalState) -> dict:
    """
    Report Agent node - generates final structured reports.

    Outputs:
    - JSON report
    - Markdown report
    - HTML report
    - PDF report (via reportlab/weasyprint)
    """
    settings = get_settings()
    thread_id = state.get("thread_id", "unknown")

    logger.info("report_agent_generating", thread_id=thread_id)

    patient_info = state.get("patient_information", {})
    patient_answers = state.get("patient_answers", [])
    clinical_summary = state.get("clinical_summary", "")
    intermediate_recommendation = state.get("intermediate_recommendation", "")
    physician_review = state.get("physician_review", {})
    physician_treatment = state.get("physician_treatment", "")
    possible_observations = state.get("possible_observations", [])

    generated_at = datetime.utcnow().isoformat()

    # JSON Report
    json_report = {
        "report_type": "Preliminary Clinical Orientation",
        "generated_at": generated_at,
        "thread_id": thread_id,
        "patient_information": patient_info,
        "patient_answers": patient_answers,
        "clinical_summary": clinical_summary,
        "intermediate_recommendation": intermediate_recommendation,
        "possible_observations": possible_observations,
        "physician_review": physician_review,
        "physician_treatment": physician_treatment,
        "disclaimer": settings.medical_disclaimer,
    }

    # Markdown Report
    markdown_report = _generate_markdown_report(
        patient_info, patient_answers, clinical_summary,
        intermediate_recommendation, physician_review,
        physician_treatment, possible_observations,
        settings.medical_disclaimer, generated_at,
    )

    # HTML Report
    html_report = _generate_html_report(
        patient_info, patient_answers, clinical_summary,
        intermediate_recommendation, physician_review,
        physician_treatment, possible_observations,
        settings.medical_disclaimer, generated_at,
    )

    # PDF Report
    pdf_path = _generate_pdf_report(
        thread_id, markdown_report, settings.medical_disclaimer,
    )

    final_report = {
        "json_report": json_report,
        "markdown_report": markdown_report,
        "html_report": html_report,
        "pdf_path": pdf_path,
        "generated_at": generated_at,
    }

    log_node_transition(logger, "report_agent", "end", thread_id)

    return {
        "final_report": final_report,
        "consultation_status": "completed",
        "next": "end",
        "messages": [
            AIMessage(content="Final report generated successfully.")
        ],
    }


def _generate_markdown_report(
    patient_info, answers, summary, recommendation,
    physician_review, treatment, observations, disclaimer, generated_at,
) -> str:
    """Generate Markdown format report."""
    lines = [
        "# MediGraph AI - Preliminary Clinical Orientation Report",
        f"\n**Generated:** {generated_at}\n",
        "## Patient Information",
        f"- **Name:** {patient_info.get('name', 'N/A')}",
        f"- **Age:** {patient_info.get('age', 'N/A')}",
        f"- **Gender:** {patient_info.get('gender', 'N/A')}",
        f"- **Medical History:** {patient_info.get('medical_history', 'N/A')}",
        f"- **Chief Complaint:** {patient_info.get('chief_complaint', 'N/A')}",
        "\n## Patient Questionnaire",
    ]

    for qa in answers:
        lines.append(f"\n**Q{qa.get('question_number')}: {qa.get('question')}**")
        lines.append(f"Answer: {qa.get('answer')}")

    lines.extend([
        "\n## Clinical Summary",
        summary,
        "\n## Intermediate Recommendation",
        recommendation,
    ])

    if physician_review:
        lines.extend([
            "\n## Physician Review",
            f"- **Approved:** {physician_review.get('approved', False)}",
            f"- **Notes:** {physician_review.get('physician_notes', 'N/A')}",
        ])

    if treatment:
        lines.extend(["\n## Physician Treatment", treatment])

    lines.extend([
        "\n## Possible Observations",
        "\n".join(f"- {obs}" for obs in observations),
        f"\n---\n\n**Disclaimer:** {disclaimer}",
    ])

    return "\n".join(lines)


def _generate_html_report(
    patient_info, answers, summary, recommendation,
    physician_review, treatment, observations, disclaimer, generated_at,
) -> str:
    """Generate HTML format report using Jinja2 template."""
    template = Template(REPORT_HTML_TEMPLATE)
    return template.render(
        patient=patient_info,
        answers=answers,
        clinical_summary=summary,
        intermediate_recommendation=recommendation,
        physician_review=physician_review,
        physician_treatment=treatment,
        observations=", ".join(observations),
        disclaimer=disclaimer,
        generated_at=generated_at,
    )


def _generate_pdf_report(thread_id: str, markdown_content: str, disclaimer: str) -> str:
    """Generate PDF report using reportlab."""
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = reports_dir / f"report_{thread_id}.pdf"

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        for line in markdown_content.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            if line.startswith("# "):
                story.append(Paragraph(line[2:], styles["Heading1"]))
            elif line.startswith("## "):
                story.append(Paragraph(line[3:], styles["Heading2"]))
            elif line.startswith("**"):
                clean = line.replace("**", "<b>").replace("**", "</b>")
                story.append(Paragraph(clean, styles["Normal"]))
            else:
                story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)
        logger.info("pdf_generated", path=str(pdf_path))
        return str(pdf_path)
    except Exception as e:
        logger.error("pdf_generation_failed", error=str(e))
        return ""
