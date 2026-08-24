"""Authorization service factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flowos.services.factory import ServiceFactory
from flowos.services.schema import ServiceType

if TYPE_CHECKING:
    from flowos_core.services.authorization.base import BaseAuthorizationService
    from flowos_core.services.settings.service import SettingsService

    from flowos.services.authorization.service import FlowOSAuthorizationService


class AuthorizationServiceFactory(ServiceFactory):
    """Factory that creates the FlowOS authorization service."""

    name = ServiceType.AUTHORIZATION_SERVICE.value

    service_class: type[FlowOSAuthorizationService]

    def __init__(self) -> None:
        """Bind the factory to the FlowOSAuthorizationService implementation."""
        from flowos.services.authorization.service import FlowOSAuthorizationService

        super().__init__(FlowOSAuthorizationService)

    def create(self, settings_service: SettingsService) -> BaseAuthorizationService:
        """Build a FlowOSAuthorizationService using the injected settings service."""
        return self.service_class(settings_service)
