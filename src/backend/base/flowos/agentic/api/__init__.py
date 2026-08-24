"""FlowOS Assistant API module."""

# Note: router is imported directly via flowos.agentic.api.router to avoid circular imports
# Use: from flowos.agentic.api.router import router
from flowos.agentic.api.schemas import AssistantRequest, StepType, ValidationResult

__all__ = ["AssistantRequest", "StepType", "ValidationResult"]
