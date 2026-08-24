from typing import Any

from flowos_core.field_typing.constants import (
    AgentExecutor,
    BaseChatMemory,
    BaseChatModel,
    BaseDocumentCompressor,
    BaseLanguageModel,
    BaseLLM,
    BaseLoader,
    BaseMemory,
    BaseOutputParser,
    BasePromptTemplate,
    BaseRetriever,
    Callable,
    Chain,
    ChatPromptTemplate,
    Code,
    Data,
    Document,
    Embeddings,
    LanguageModel,
    NestedDict,
    Object,
    PromptTemplate,
    Retriever,
    Text,
    TextSplitter,
    Tool,
    VectorStore,
)
from flowos_core.field_typing.range_spec import RangeSpec


def _import_input_class():
    from flowos_core.template.field.base import Input

    return Input


def _import_output_class():
    from flowos_core.template.field.base import Output

    return Output


def __getattr__(name: str) -> Any:
    # This is to avoid circular imports
    if name == "Input":
        return _import_input_class()
    if name == "Output":
        return _import_output_class()
    if name == "RangeSpec":
        return RangeSpec
    # The other names should work as if they were imported from constants
    # Import the constants module flowos.field_typing.constants
    from . import constants

    return getattr(constants, name)


__all__ = [
    "AgentExecutor",
    "BaseChatMemory",
    "BaseChatModel",
    "BaseDocumentCompressor",
    "BaseLLM",
    "BaseLanguageModel",
    "BaseLoader",
    "BaseMemory",
    "BaseOutputParser",
    "BasePromptTemplate",
    "BaseRetriever",
    "Callable",
    "Chain",
    "ChatPromptTemplate",
    "Code",
    "Data",
    "Document",
    "Embeddings",
    "LanguageModel",
    "NestedDict",
    "Object",
    "PromptTemplate",
    "RangeSpec",
    "Retriever",
    "Text",
    "TextSplitter",
    "Tool",
    "VectorStore",
]
