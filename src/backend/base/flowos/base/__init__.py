"""Backwards compatibility module for flowos.base.

This module imports from flowos_core.base to maintain compatibility with existing code
that expects to import from flowos.base.
"""

# Import all base modules from flowos_core for backwards compatibility
from flowos_core.base import *  # noqa: F403
