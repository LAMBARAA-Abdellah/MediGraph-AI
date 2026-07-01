"""Structured logging configuration for MediGraph AI."""

import logging
import sys
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generator, Optional

import structlog

from backend.app.config import get_settings


def setup_logging() -> None:
    """Configure structlog and standard logging."""
    settings = get_settings()
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a named logger instance."""
    return structlog.get_logger(name)


@contextmanager
def log_execution_time(logger: structlog.BoundLogger, operation: str) -> Generator[None, None, None]:
    """Context manager to log execution time of an operation."""
    start = time.perf_counter()
    logger.info(f"{operation}_started")
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{operation}_completed", execution_time_seconds=round(elapsed, 4))


def log_node_transition(
    logger: structlog.BoundLogger,
    from_node: str,
    to_node: str,
    thread_id: Optional[str] = None,
) -> None:
    """Log LangGraph node transition."""
    logger.info(
        "node_transition",
        from_node=from_node,
        to_node=to_node,
        thread_id=thread_id,
    )


def log_llm_call(logger: structlog.BoundLogger, model: str, prompt_tokens: int = 0) -> None:
    """Log LLM API call."""
    logger.info("llm_call", model=model, prompt_tokens=prompt_tokens)


def log_tool_call(logger: structlog.BoundLogger, tool_name: str, **kwargs: Any) -> None:
    """Log tool invocation."""
    logger.info("tool_call", tool_name=tool_name, **kwargs)


def timed(logger_name: str = "medigraph") -> Callable:
    """Decorator to log function execution time."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(logger_name)
            with log_execution_time(logger, func.__name__):
                return func(*args, **kwargs)

        return wrapper

    return decorator
