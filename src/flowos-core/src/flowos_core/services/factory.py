"""Base service factory classes for flowos_core package."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flowos_core.services.base import Service


class ServiceFactory(ABC):
    """Base service factory class."""

    def __init__(self):
        self.service_class = None
        self.dependencies = []

    @abstractmethod
    def create(self, **kwargs) -> "Service":
        """Create a service instance."""
