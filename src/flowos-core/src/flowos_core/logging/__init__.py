"""Backwards compatibility module for flowos_core.logging.

This module provides backwards compatibility for code that imports from flowos_core.logging.
All functionality has been moved to flowos_core.log.
"""

# Re-export everything from flowos_core.log for backwards compatibility
from flowos_core.log.logger import configure, logger

# Maintain the same __all__ exports
__all__ = ["configure", "logger"]
