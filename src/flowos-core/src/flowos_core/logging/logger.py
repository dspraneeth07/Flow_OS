"""Backwards compatibility module for flowos_core.logging.logger.

This module provides backwards compatibility for code that imports from flowos_core.logging.logger.
All functionality has been moved to flowos_core.log.logger.
"""

# Ensure we maintain all the original exports
from flowos_core.log.logger import (
    InterceptHandler,
    LogConfig,
    configure,
    logger,
    setup_gunicorn_logger,
    setup_uvicorn_logger,
)

__all__ = [
    "InterceptHandler",
    "LogConfig",
    "configure",
    "logger",
    "setup_gunicorn_logger",
    "setup_uvicorn_logger",
]
