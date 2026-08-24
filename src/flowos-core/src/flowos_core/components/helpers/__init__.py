"""Helpers module - backwards compatibility for moved components."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from flowos_core.components._importing import import_mod

if TYPE_CHECKING:
    from flowos_core.components.helpers.calculator_core import CalculatorComponent
    from flowos_core.components.helpers.create_list import CreateListComponent
    from flowos_core.components.helpers.current_date import CurrentDateComponent
    from flowos_core.components.helpers.id_generator import IDGeneratorComponent
    from flowos_core.components.helpers.memory import MemoryComponent
    from flowos_core.components.helpers.output_parser import OutputParserComponent
    from flowos_core.components.helpers.store_message import MessageStoreComponent

_dynamic_imports = {
    "CalculatorComponent": "calculator_core",
    "CreateListComponent": "create_list",
    "CurrentDateComponent": "current_date",
    "IDGeneratorComponent": "id_generator",
    "MemoryComponent": "memory",
    "OutputParserComponent": "output_parser",
    "MessageStoreComponent": "store_message",
}

__all__ = [
    "CalculatorComponent",
    "CreateListComponent",
    "CurrentDateComponent",
    "IDGeneratorComponent",
    "MemoryComponent",
    "MessageStoreComponent",
    "OutputParserComponent",
]

# Register redirected submodules in sys.modules for direct importlib.import_module() calls
# This allows imports like: import flowos_core.components.helpers.current_date
_redirected_submodules = {
    "flowos_core.components.helpers.current_date": "flowos_core.components.utilities.current_date",
    "flowos_core.components.helpers.calculator_core": "flowos_core.components.utilities.calculator_core",
    "flowos_core.components.helpers.id_generator": "flowos_core.components.utilities.id_generator",
    "flowos_core.components.helpers.memory": "flowos_core.components.models_and_agents.memory",
}

for old_path, new_path in _redirected_submodules.items():
    if old_path not in sys.modules:
        # Use a lazy loader that imports the actual module when accessed
        class _RedirectedModule:
            def __init__(self, target_path: str, original_path: str):
                self._target_path = target_path
                self._original_path = original_path
                self._module = None

            def __getattr__(self, name: str) -> Any:
                if self._module is None:
                    from importlib import import_module

                    self._module = import_module(self._target_path)
                    # Also register under the original path for future imports
                    sys.modules[self._original_path] = self._module
                return getattr(self._module, name)

            def __repr__(self) -> str:
                return f"<redirected module '{self._original_path}' -> '{self._target_path}'>"

        sys.modules[old_path] = _RedirectedModule(new_path, old_path)


def __getattr__(attr_name: str) -> Any:
    """Lazily import helper components on attribute access."""
    # Handle submodule access for backwards compatibility
    # e.g., flowos_core.components.helpers.id_generator -> flowos_core.components.utilities.id_generator
    if attr_name == "id_generator":
        from importlib import import_module

        result = import_module("flowos_core.components.utilities.id_generator")
        globals()[attr_name] = result
        return result
    if attr_name == "calculator_core":
        from importlib import import_module

        result = import_module("flowos_core.components.utilities.calculator_core")
        globals()[attr_name] = result
        return result
    if attr_name == "current_date":
        from importlib import import_module

        result = import_module("flowos_core.components.utilities.current_date")
        globals()[attr_name] = result
        return result
    if attr_name == "memory":
        from importlib import import_module

        result = import_module("flowos_core.components.models_and_agents.memory")
        globals()[attr_name] = result
        return result

    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)

    # CurrentDateComponent, CalculatorComponent, and IDGeneratorComponent were moved to utilities
    # Forward them to utilities for backwards compatibility
    if attr_name in ("CurrentDateComponent", "CalculatorComponent", "IDGeneratorComponent"):
        from flowos_core.components import utilities

        result = getattr(utilities, attr_name)
        globals()[attr_name] = result
        return result

    # MemoryComponent was moved to models_and_agents
    # Forward it to models_and_agents for backwards compatibility
    if attr_name == "MemoryComponent":
        from flowos_core.components import models_and_agents

        result = getattr(models_and_agents, attr_name)
        globals()[attr_name] = result
        return result

    # CreateListComponent, MessageStoreComponent, and OutputParserComponent were moved to processing
    # Forward them to processing for backwards compatibility
    if attr_name == "CreateListComponent":
        from flowos_core.components import processing

        result = getattr(processing, attr_name)
        globals()[attr_name] = result
        return result
    if attr_name == "MessageStoreComponent":
        from flowos_core.components import processing

        result = processing.MessageStoreComponent
        globals()[attr_name] = result
        return result
    if attr_name == "OutputParserComponent":
        from flowos_core.components import processing

        result = getattr(processing, attr_name)
        globals()[attr_name] = result
        return result

    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
