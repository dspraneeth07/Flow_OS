"""FlowOS environment utility functions."""

import importlib.util

from flowos_core.log.logger import logger


class _FlowOSModule:
    # Static variable
    # Tri-state:
    # - None: FlowOS check not performed yet
    # - True: FlowOS is available
    # - False: FlowOS is not available
    _available = None

    @classmethod
    def is_available(cls):
        return cls._available

    @classmethod
    def set_available(cls, value):
        cls._available = value


def has_flowos_memory():
    """Check if flowos.memory (with database support) and MessageTable are available."""
    # TODO: REVISIT: Optimize this implementation later
    # - Consider refactoring to use lazy loading or a more robust service discovery mechanism
    #   that can handle runtime availability changes.

    # Use cached check from previous invocation (if applicable)

    is_flowos_available = _FlowOSModule.is_available()

    if is_flowos_available is not None:
        return is_flowos_available

    # First check (lazy load and cache check)

    module_spec = None

    try:
        module_spec = importlib.util.find_spec("flowos")
    except ImportError:
        pass
    except (TypeError, ValueError) as e:
        logger.error(f"Error encountered checking for flowos.memory: {e}")

    is_flowos_available = module_spec is not None
    _FlowOSModule.set_available(is_flowos_available)

    return is_flowos_available


def has_flowos_db_backend() -> bool:
    """Return True iff flowos-backed memory calls have a real DB to hit.

    Requires both flowos to be importable AND the registered database
    service to be a non-noop implementation. Evaluated on every call because
    the database service is typically registered *after* this module is first
    imported (e.g., from Component class definitions loaded before graph setup).
    """
    if not has_flowos_memory():
        return False
    from flowos_core.services.database.service import NoopDatabaseService
    from flowos_core.services.deps import get_db_service

    try:
        return not isinstance(get_db_service(), NoopDatabaseService)
    except Exception:  # noqa: BLE001
        return False
