"""Message class for flowos - imports from flowos_core.

This maintains backward compatibility while using the flowos_core implementation.
"""

# Import and re-export to ensure class identity is preserved
from flowos_core.schema.message import (
    MAX_ATTACHMENT_SIZE_BYTES,
    ContentBlock,
    DefaultModel,
    ErrorMessage,
    Message,
    MessageResponse,
)

__all__ = [
    "MAX_ATTACHMENT_SIZE_BYTES",
    "ContentBlock",
    "DefaultModel",
    "ErrorMessage",
    "Message",
    "MessageResponse",
]
