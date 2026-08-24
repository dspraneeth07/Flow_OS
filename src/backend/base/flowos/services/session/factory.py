from typing import TYPE_CHECKING

from typing_extensions import override

from flowos.services.factory import ServiceFactory
from flowos.services.session.service import SessionService

if TYPE_CHECKING:
    from flowos.services.cache.service import CacheService


class SessionServiceFactory(ServiceFactory):
    def __init__(self) -> None:
        super().__init__(SessionService)

    @override
    def create(self, cache_service: "CacheService"):
        return SessionService(cache_service)
