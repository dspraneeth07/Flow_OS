"""Exceptions raised by the FlowOS SDK."""

from __future__ import annotations


class FlowOSError(Exception):
    """Base class for all FlowOS SDK errors."""


class FlowOSHTTPError(FlowOSError):
    """An HTTP error was returned by the FlowOS API."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class FlowOSNotFoundError(FlowOSHTTPError):
    """The requested resource was not found (404)."""


class FlowOSAuthError(FlowOSHTTPError):
    """Authentication failed (401/403)."""


class FlowOSValidationError(FlowOSHTTPError):
    """The request payload was rejected by the server (422)."""


class FlowOSConnectionError(FlowOSError):
    """Could not connect to the FlowOS instance."""


class FlowOSTimeoutError(FlowOSError):
    """A background job or polling operation exceeded its timeout.

    Adapted from ``FlowOSV2TimeoutError`` in flowos-ai/sdk PR #1
    (Janardan Singh Kavia, IBM Corp., Apache 2.0).
    """


class EnvironmentNotFoundError(FlowOSError):
    """The named environment is not defined in the environments config."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"Environment {name!r} not found. Check your flowos-environments.toml (or FLOWOS_ENV variable)."
        )


class EnvironmentConfigError(FlowOSError):
    """The environments config file is malformed or missing required fields."""
