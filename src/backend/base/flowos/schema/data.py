"""JSON and Data classes for flowos - imports from flowos_core.

This maintains backward compatibility while using the flowos_core implementation.
JSON is the new base type; Data is an alias for backwards compatibility.
"""

from flowos_core.schema.data import JSON, Data, custom_serializer, serialize_data

__all__ = ["JSON", "Data", "custom_serializer", "serialize_data"]
