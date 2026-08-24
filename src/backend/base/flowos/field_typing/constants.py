# Re-export everything from flowos_core.field_typing.constants for backward compatibility
# Import additional types
from collections.abc import Callable
from typing import Text

from flowos_core.field_typing.constants import (
    CUSTOM_COMPONENT_SUPPORTED_TYPES,
    DEFAULT_IMPORT_STRING,
    LANGCHAIN_BASE_TYPES,
    # Import all the langchain types that may be needed
    AgentExecutor,
    BaseChatMemory,
    BaseChatMessageHistory,
    BaseChatModel,
    BaseDocumentCompressor,
    BaseLanguageModel,
    BaseLLM,
    BaseLLMOutputParser,
    BaseLoader,
    BaseMemory,
    BaseOutputParser,
    BasePromptTemplate,
    BaseRetriever,
    BaseTool,
    Chain,
    ChatPromptTemplate,
    Code,
    Document,
    Embeddings,
    LanguageModel,
    Memory,
    NestedDict,
    Object,
    OutputParser,
    PromptTemplate,
    Retriever,
    TextSplitter,
    Tool,
    ToolEnabledLanguageModel,
    VectorStore,
    VectorStoreRetriever,
)

# Import flowos_core schema types
from flowos_core.schema.data import Data
from flowos_core.schema.dataframe import DataFrame

# Import Message from flowos.schema for backward compatibility
from flowos.schema.message import Message

# Add Message and DataFrame to CUSTOM_COMPONENT_SUPPORTED_TYPES
CUSTOM_COMPONENT_SUPPORTED_TYPES = {
    **CUSTOM_COMPONENT_SUPPORTED_TYPES,
    "Message": Message,
    "DataFrame": DataFrame,
}

__all__ = [
    "CUSTOM_COMPONENT_SUPPORTED_TYPES",
    "DEFAULT_IMPORT_STRING",
    "LANGCHAIN_BASE_TYPES",
    # Langchain types
    "AgentExecutor",
    "BaseChatMemory",
    "BaseChatMessageHistory",
    "BaseChatModel",
    "BaseDocumentCompressor",
    "BaseLLM",
    "BaseLLMOutputParser",
    "BaseLanguageModel",
    "BaseLoader",
    "BaseMemory",
    "BaseOutputParser",
    "BasePromptTemplate",
    "BaseRetriever",
    "BaseTool",
    # Additional types
    "Callable",
    "Chain",
    "ChatPromptTemplate",
    "Code",
    "Data",
    "DataFrame",
    "Document",
    "Embeddings",
    "LanguageModel",
    "Memory",
    "Message",
    "NestedDict",
    "Object",
    "OutputParser",
    "PromptTemplate",
    "Retriever",
    "Text",
    "TextSplitter",
    "Tool",
    "ToolEnabledLanguageModel",
    "VectorStore",
    "VectorStoreRetriever",
]
