"""Tests for field_typing lazy import mechanism.

These tests verify that the __getattr__ lazy import pattern in field_typing/__init__.py
works correctly and returns the expected types.
"""

import sys
import types

import pytest


class TestFieldTypingLazyImports:
    """Test that field_typing exports are accessible via lazy imports."""

    def test_input_import(self):
        """Test that Input can be imported from field_typing."""
        from flowos_core.field_typing import Input
        from flowos_core.template.field.base import Input as DirectInput

        assert Input is DirectInput

    def test_output_import(self):
        """Test that Output can be imported from field_typing."""
        from flowos_core.field_typing import Output
        from flowos_core.template.field.base import Output as DirectOutput

        assert Output is DirectOutput

    def test_range_spec_import(self):
        """Test that RangeSpec can be imported from field_typing."""
        from flowos_core.field_typing import RangeSpec
        from flowos_core.field_typing.range_spec import RangeSpec as DirectRangeSpec

        assert RangeSpec is DirectRangeSpec

    def test_data_import(self):
        """Test that Data can be imported from field_typing."""
        from flowos_core.field_typing import Data
        from flowos_core.schema.data import Data as DirectData

        assert Data is DirectData

    def test_constants_imports(self):
        """Test that constants from langchain are accessible."""
        from flowos_core.field_typing import (
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
            Chain,
            ChatPromptTemplate,
            Document,
            Embeddings,
            PromptTemplate,
            TextSplitter,
            Tool,
            VectorStore,
        )

        # Verify they are not None (actual types or stubs)
        assert AgentExecutor is not None
        assert BaseChatMemory is not None
        assert BaseChatModel is not None
        assert BaseDocumentCompressor is not None
        assert BaseLanguageModel is not None
        assert BaseLLM is not None
        assert BaseLoader is not None
        assert BaseMemory is not None
        assert BaseOutputParser is not None
        assert BasePromptTemplate is not None
        assert BaseRetriever is not None
        assert Chain is not None
        assert ChatPromptTemplate is not None
        assert Document is not None
        assert Embeddings is not None
        assert PromptTemplate is not None
        assert TextSplitter is not None
        assert Tool is not None
        assert VectorStore is not None

    def test_type_aliases_import(self):
        """Test that type aliases are accessible."""
        from flowos_core.field_typing import (
            Callable,
            Code,
            LanguageModel,
            NestedDict,
            Object,
            Retriever,
            Text,
        )

        assert Callable is not None
        assert Code is not None
        assert LanguageModel is not None
        assert NestedDict is not None
        assert Object is not None
        assert Retriever is not None
        assert Text is not None

    def test_invalid_attribute_raises_error(self):
        """Test that accessing invalid attribute raises AttributeError."""
        import flowos_core.field_typing

        with pytest.raises(AttributeError, match="has no attribute 'NonExistentType'"):
            _ = flowos_core.field_typing.NonExistentType

    def test_all_exports_are_accessible(self):
        """Test that all items in __all__ are accessible."""
        import flowos_core.field_typing

        for name in flowos_core.field_typing.__all__:
            attr = getattr(flowos_core.field_typing, name)
            assert attr is not None, f"{name} should be accessible"

    def test_repeated_access_returns_same_object(self):
        """Test that repeated access returns the same object (caching works)."""
        from flowos_core.field_typing import Data as Data1
        from flowos_core.field_typing import Data as Data2

        assert Data1 is Data2

    def test_constants_match_direct_imports(self):
        """Test that constants from field_typing match direct imports from constants module."""
        from flowos_core.field_typing import Data, Document, Object
        from flowos_core.field_typing.constants import Data as DirectData
        from flowos_core.field_typing.constants import Document as DirectDocument
        from flowos_core.field_typing.constants import Object as DirectObject

        assert Data is DirectData
        assert Document is DirectDocument
        assert Object is DirectObject


class TestFieldTypingNativeDependencyFailure:
    """Test that constants module survives native-dependency failures during import.

    Reproduces the production crash where PyTorch's `c10.dll` fails to load on a
    fresh Windows install missing the Microsoft Visual C++ Redistributable. The
    OSError raised by `torch._load_dll_libraries()` propagates upward through:

        transformers (imports torch) →
        langchain_core.language_models.base (imports `from transformers import GPT2TokenizerFast`) →
        langchain_core.language_models →
        langchain_classic.agents.agent →
        langchain_classic.agents →
        flowos_core.field_typing.constants line 9 (`from langchain_classic.agents import AgentExecutor`)

    `flowos_core.field_typing.constants` already wraps its langchain imports in a
    `try/except ImportError` with stub-class fallbacks for the "langchain not
    installed" case. This test asserts the same fallback path also activates when
    a native-dependency failure surfaces as `OSError` instead of `ImportError`.
    """

    def test_should_use_stub_classes_when_langchain_import_raises_oserror(self, monkeypatch):
        """Bug: `flowos --version` crashes on fresh Windows because flowos_core fails to import.

        Cause: `c10.dll` raises `OSError: [WinError 126]` and the existing fallback
        only catches `ImportError`. After fix: stub classes are used and flowos_core loads
        cleanly, allowing the Desktop install verification to succeed even when
        torch's native deps are unavailable.
        """

        class _RaisingLangchainAgents(types.ModuleType):
            """Stand-in for langchain_classic.agents.

            Mimics the c10.dll OSError surfacing through
            `from langchain_classic.agents import X`.
            """

            def __getattr__(self, name: str):
                if name.startswith("__"):
                    raise AttributeError(name)
                msg = (
                    "[WinError 126] The specified module could not be found. "
                    r'Error loading "torch\lib\c10.dll" or one of its dependencies.'
                )
                raise OSError(msg)

        # Arrange — install the raising mock and force a clean reload of the target module
        monkeypatch.setitem(
            sys.modules,
            "langchain_classic.agents",
            _RaisingLangchainAgents("langchain_classic.agents"),
        )
        monkeypatch.delitem(sys.modules, "flowos_core.field_typing.constants", raising=False)
        monkeypatch.delitem(sys.modules, "flowos_core.field_typing", raising=False)

        # Act — must not raise (this is the regression guard)
        from flowos_core.field_typing import constants

        # Assert — the in-module stub class is what's exposed, not the real one
        assert constants.AgentExecutor is not None
        assert constants.AgentExecutor.__module__ == "flowos_core.field_typing.constants"
        assert "AgentExecutor" in constants.LANGCHAIN_BASE_TYPES
        assert constants.LANGCHAIN_BASE_TYPES["AgentExecutor"] is constants.AgentExecutor


class TestFieldTypingModuleStructure:
    """Test the structure of the field_typing module."""

    def test_all_list_exists(self):
        """Test that __all__ is defined."""
        import flowos_core.field_typing

        assert hasattr(flowos_core.field_typing, "__all__")
        assert isinstance(flowos_core.field_typing.__all__, list)
        assert len(flowos_core.field_typing.__all__) > 0

    def test_getattr_function_exists(self):
        """Test that __getattr__ is defined for lazy loading."""
        import flowos_core.field_typing

        # The module should have __getattr__ defined
        # We verify this indirectly by checking we can access lazy attributes
        assert hasattr(flowos_core.field_typing, "Input") or "Input" in flowos_core.field_typing.__all__

    def test_constants_names_set_exists(self):
        """Test that _CONSTANTS_NAMES is defined."""
        import flowos_core.field_typing

        assert hasattr(flowos_core.field_typing, "_CONSTANTS_NAMES")
        assert isinstance(flowos_core.field_typing._CONSTANTS_NAMES, set)
