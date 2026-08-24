"""Custom exception types for FlowOS integration."""


class FlowOSIntegrationError(Exception):
    """Base exception for FlowOS integration errors."""

    pass


class ConversionError(FlowOSIntegrationError):
    """Error during FlowOS to Stepflow conversion."""

    pass


class ValidationError(FlowOSIntegrationError):
    """Error during workflow validation."""

    pass


class ExecutionError(FlowOSIntegrationError):
    """Error during component execution."""

    pass
