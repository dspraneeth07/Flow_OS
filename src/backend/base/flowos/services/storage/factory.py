from flowos_core.log.logger import logger
from flowos_core.services.settings.service import SettingsService
from typing_extensions import override

from flowos.services.factory import ServiceFactory
from flowos.services.session.service import SessionService
from flowos.services.storage.service import StorageService


class StorageServiceFactory(ServiceFactory):
    def __init__(self) -> None:
        super().__init__(
            StorageService,
        )

    @override
    def create(self, session_service: SessionService, settings_service: SettingsService):
        storage_type = settings_service.settings.storage_type
        if storage_type.lower() == "local":
            from .local import LocalStorageService

            return LocalStorageService(session_service, settings_service)
        if storage_type.lower() == "s3":
            from .s3 import S3StorageService

            return S3StorageService(session_service, settings_service)
        logger.warning(f"Storage type {storage_type} not supported. Using local storage.")
        from .local import LocalStorageService

        return LocalStorageService(session_service, settings_service)
