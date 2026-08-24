"""FLOWOS_CORE authorization service package (abstract base + default no-op allow-all implementation)."""

from flowos_core.services.authorization.base import BaseAuthorizationService
from flowos_core.services.authorization.service import AuthorizationService

__all__ = ["AuthorizationService", "BaseAuthorizationService"]
