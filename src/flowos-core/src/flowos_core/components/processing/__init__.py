"""Processing components for FlowOS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flowos_core.components._importing import import_mod

if TYPE_CHECKING:
    from flowos_core.components.processing.combine_text import CombineTextComponent
    from flowos_core.components.processing.converter import TypeConverterComponent
    from flowos_core.components.processing.create_list import CreateListComponent
    from flowos_core.components.processing.data_operations import DataOperationsComponent
    from flowos_core.components.processing.dataframe_operations import DataFrameOperationsComponent
    from flowos_core.components.processing.json_cleaner import JSONCleaner
    from flowos_core.components.processing.output_parser import OutputParserComponent
    from flowos_core.components.processing.parse_data import ParseDataComponent
    from flowos_core.components.processing.parser import ParserComponent
    from flowos_core.components.processing.regex import RegexExtractorComponent
    from flowos_core.components.processing.split_text import SplitTextComponent
    from flowos_core.components.processing.store_message import MessageStoreComponent

_dynamic_imports = {
    "CombineTextComponent": "combine_text",
    "TypeConverterComponent": "converter",
    "CreateListComponent": "create_list",
    "DataOperationsComponent": "data_operations",
    "DataFrameOperationsComponent": "dataframe_operations",
    "JSONCleaner": "json_cleaner",
    "OutputParserComponent": "output_parser",
    "ParseDataComponent": "parse_data",
    "ParserComponent": "parser",
    "RegexExtractorComponent": "regex",
    "SplitTextComponent": "split_text",
    "MessageStoreComponent": "store_message",
}

__all__ = [
    "CombineTextComponent",
    "CreateListComponent",
    "DataFrameOperationsComponent",
    "DataOperationsComponent",
    "JSONCleaner",
    "MessageStoreComponent",
    "OutputParserComponent",
    "ParseDataComponent",
    "ParserComponent",
    "RegexExtractorComponent",
    "SplitTextComponent",
    "TypeConverterComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import processing components on attribute access."""
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
