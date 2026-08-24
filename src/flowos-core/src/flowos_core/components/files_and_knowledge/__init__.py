from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flowos_core.components._importing import import_mod

if TYPE_CHECKING:
    from flowos_core.components.files_and_knowledge.directory import DirectoryComponent
    from flowos_core.components.files_and_knowledge.file import FileComponent
    from flowos_core.components.files_and_knowledge.filesystem import FileSystemToolComponent
    from flowos_core.components.files_and_knowledge.ingestion import KnowledgeIngestionComponent
    from flowos_core.components.files_and_knowledge.knowledge import KnowledgeComponent
    from flowos_core.components.files_and_knowledge.memory_retrieval import MemoryBaseComponent
    from flowos_core.components.files_and_knowledge.retrieval import KnowledgeBaseComponent
    from flowos_core.components.files_and_knowledge.save_file import SaveToFileComponent


_dynamic_imports = {
    "DirectoryComponent": "directory",
    "FileComponent": "file",
    "FileSystemToolComponent": "filesystem",
    "KnowledgeComponent": "knowledge",
    "KnowledgeIngestionComponent": "ingestion",
    "KnowledgeBaseComponent": "retrieval",
    "MemoryBaseComponent": "memory_retrieval",
    "SaveToFileComponent": "save_file",
}

__all__ = [
    "DirectoryComponent",
    "FileComponent",
    "FileSystemToolComponent",
    "KnowledgeBaseComponent",
    "KnowledgeComponent",
    "KnowledgeIngestionComponent",
    "MemoryBaseComponent",
    "SaveToFileComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import files and knowledge components on attribute access."""
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
