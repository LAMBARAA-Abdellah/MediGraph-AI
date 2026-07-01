"""LangGraph StateGraph definition with checkpoint persistence."""

import os
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from backend.app.config import get_settings
from backend.app.middleware.logging_middleware import get_logger
from backend.app.nodes.diagnostic_agent import diagnostic_agent_node, route_from_diagnostic
from backend.app.nodes.physician_review import physician_review_node, route_from_physician_review
from backend.app.nodes.report_agent import report_agent_node
from backend.app.nodes.supervisor import route_from_supervisor, supervisor_node
from backend.app.state import MedicalState

logger = get_logger("graph")


def _create_checkpointer() -> SqliteSaver:
    """Create SQLite checkpointer for workflow persistence."""
    settings = get_settings()
    checkpoint_dir = Path(settings.langgraph_checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    db_path = checkpoint_dir / "checkpoints.db"

    import sqlite3
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    return SqliteSaver(conn)


def build_graph() -> StateGraph:
    """
    Build the MediGraph AI LangGraph workflow.

    Graph structure:
        supervisor → diagnostic_agent → supervisor (loop for questions)
        diagnostic_agent → physician_review (after 5 questions)
        physician_review → report_agent (after approval) [INTERRUPT]
        report_agent → END
    """
    workflow = StateGraph(MedicalState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("diagnostic_agent", diagnostic_agent_node)
    workflow.add_node("physician_review", physician_review_node)
    workflow.add_node("report_agent", report_agent_node)

    # Entry point
    workflow.set_entry_point("supervisor")

    # Conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "__end__": END,
        },
    )

    # Diagnostic agent routes back to supervisor or to physician review
    workflow.add_conditional_edges(
        "diagnostic_agent",
        route_from_diagnostic,
        {
            "supervisor": "supervisor",
            "physician_review": "physician_review",
        },
    )

    # Physician review - human in the loop interrupt
    workflow.add_conditional_edges(
        "physician_review",
        route_from_physician_review,
        {
            "report_agent": "report_agent",
            "__end__": END,
        },
    )

    # Report agent ends workflow
    workflow.add_edge("report_agent", END)

    return workflow


def compile_graph():
    """Compile graph with checkpointer and interrupt before physician review."""
    workflow = build_graph()
    checkpointer = _create_checkpointer()

    compiled = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["physician_review"],
    )

    logger.info("graph_compiled", interrupt_nodes=["physician_review"])
    return compiled


# Export compiled graph for LangGraph Studio
graph = compile_graph()
