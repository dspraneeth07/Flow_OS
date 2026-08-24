"""Logical groupings of FlowOS settings.

Each module defines a ``BaseModel`` mixin that owns a cohesive subset of fields
plus their intra-group validators. They are composed into the final
``Settings`` class in :mod:`flowos_core.services.settings.base`.

Mixins inherit from ``BaseModel`` (not ``BaseSettings``) and are not intended
to be instantiated directly.
"""

from flowos_core.services.settings.groups.cache import CacheSettings
from flowos_core.services.settings.groups.components import ComponentsSettings
from flowos_core.services.settings.groups.database import DatabaseSettings
from flowos_core.services.settings.groups.mcp import McpSettings
from flowos_core.services.settings.groups.observability import ObservabilitySettings
from flowos_core.services.settings.groups.paths import PathSettings
from flowos_core.services.settings.groups.runtime import RuntimeSettings
from flowos_core.services.settings.groups.security import SecuritySettings
from flowos_core.services.settings.groups.server import ServerSettings
from flowos_core.services.settings.groups.storage import StorageSettings
from flowos_core.services.settings.groups.telemetry import TelemetrySettings
from flowos_core.services.settings.groups.ui import UiSettings
from flowos_core.services.settings.groups.variables import VariablesSettings

__all__ = [
    "CacheSettings",
    "ComponentsSettings",
    "DatabaseSettings",
    "McpSettings",
    "ObservabilitySettings",
    "PathSettings",
    "RuntimeSettings",
    "SecuritySettings",
    "ServerSettings",
    "StorageSettings",
    "TelemetrySettings",
    "UiSettings",
    "VariablesSettings",
]
