"""Compatibility layer for flowos_core.components.models.

This module redirects imports to flowos_core.components.models_and_agents for backward compatibility.
"""

from __future__ import annotations

from typing import Any

# Import everything from models_and_agents to maintain backward compatibility
from flowos_core.components.models_and_agents import *  # noqa: F403
from flowos_core.components.models_and_agents import __all__  # noqa: F401


# Set up module-level __getattr__ to handle dynamic imports
def __getattr__(attr_name: str) -> Any:
    """Redirect all attribute access to models_and_agents module."""
    from flowos_core.components import models_and_agents

    if hasattr(models_and_agents, attr_name):
        return getattr(models_and_agents, attr_name)

    msg = f"module '{__name__}' has no attribute '{attr_name}'"
    raise AttributeError(msg)


def __dir__() -> list[str]:
    """Return the directory of available attributes."""
    from flowos_core.components import models_and_agents

    return dir(models_and_agents)
