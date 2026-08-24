# Backwards compatibility module for flowos.schema.graph
# This module redirects imports to the new flowos_core.schema.graph module

from flowos_core.schema.graph import InputValue, Tweaks

__all__ = ["InputValue", "Tweaks"]
