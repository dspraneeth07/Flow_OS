"""Initialize services for flowos_core package."""

from flowos_core.services.settings.factory import SettingsServiceFactory


def initialize_services():
    """Initialize required services for flowos_core."""
    from flowos_core.services.manager import get_service_manager

    # Register the settings service factory
    service_manager = get_service_manager()
    service_manager.register_factory(SettingsServiceFactory())

    # Ensure built-in pluggable services are registered (decorator runs on import).
    # This allows FLOWOS_CORE to use minimal auth/telemetry/tracing/variable when no config overrides.

    # Note: We don't create the service immediately,
    # it will be created on first use via get_settings_service()


# Initialize services when the module is imported
initialize_services()
