# Backwards compatibility module for flowos.events.event_manager
# This module redirects imports to the new flowos_core.events.event_manager module

from flowos_core.events.event_manager import (
    EventCallback,
    EventManager,
    PartialEventCallback,
    create_default_event_manager,
    create_stream_tokens_event_manager,
)

__all__ = [
    "EventCallback",
    "EventManager",
    "PartialEventCallback",
    "create_default_event_manager",
    "create_stream_tokens_event_manager",
]
