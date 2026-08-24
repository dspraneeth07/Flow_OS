"""Transaction service implementations for flowos_core."""

from __future__ import annotations

from typing import Any

from flowos_core.services.interfaces import TransactionServiceProtocol


class NoopTransactionService(TransactionServiceProtocol):
    """No-operation transaction service for standalone flowos_core mode.

    This service is used when flowos_core runs without a concrete transaction
    service implementation (e.g., without flowos). All operations
    are no-ops and transaction logging is disabled.
    """

    async def log_transaction(
        self,
        flow_id: str,
        vertex_id: str,
        inputs: dict[str, Any] | None,
        outputs: dict[str, Any] | None,
        status: str,
        target_id: str | None = None,
        error: str | None = None,
    ) -> None:
        """No-op implementation of transaction logging.

        In standalone mode, transactions are not persisted.
        """

    def is_enabled(self) -> bool:
        """Transaction logging is disabled in noop mode."""
        return False
