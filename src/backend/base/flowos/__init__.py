"""FlowOS backwards compatibility layer.

This module provides backwards compatibility by forwarding imports from
flowos.* to flowos_core.* to maintain compatibility with existing code that
references the old flowos module structure.
"""

from flowos.helpers.windows_postgres_helper import configure_windows_postgres_event_loop

configure_windows_postgres_event_loop(source="package_init")

import importlib  # noqa: E402
import importlib.abc  # noqa: E402
import importlib.machinery  # noqa: E402
import importlib.util  # noqa: E402
import sys  # noqa: E402
from types import ModuleType  # noqa: E402
from typing import Any  # noqa: E402

# ---------------------------------------------------------------------------
# Dynamic ``flowos.components.*`` -> ``flowos_core.components.*`` bridge
# ---------------------------------------------------------------------------
#
# Saved flows in the wild import their components via ``flowos.components.<sub>``
# (``from flowos.components.processing.converter import convert_to_dataframe``,
# ``import flowos.components.knowledge_bases.retrieval``, etc.).  The flowos_core
# extraction moved every component module into ``flowos_core.components.*``; we
# previously kept a stack of physical shim files (one per subpackage)
# under ``src/backend/base/flowos/components/`` to forward those imports.
# Maintaining one shim file per subpackage does not scale -- every new flowos_core
# component requires a parallel flowos shim, and forgetting to add one
# silently breaks pre-existing flows at load time.
#
# Replace the physical-shim stack with a single meta path finder that
# dynamically resolves any ``flowos.components.<rest>`` import to the
# corresponding ``flowos_core.components.<rest>`` module.  The finder returns the
# already-loaded flowos_core module from ``create_module`` so the flowos- and
# flowos_core-prefixed names share a single underlying module object; class
# identity is preserved across the bridge (critical for ``isinstance``
# checks against types resolved through either path).
#
# Special-case overrides cover the few subpackages whose name diverged
# during the move (e.g. ``knowledge_bases`` -> ``files_and_knowledge``).


class _FlowOSComponentsAliasLoader(importlib.abc.Loader):
    """Loader that fronts ``flowos_core.components.<rest>`` as ``flowos.components.<rest>``.

    ``create_module`` returns the flowos_core module object directly so attribute
    access on either name resolves to the same backing module.
    ``exec_module`` is intentionally a no-op because the flowos_core module is
    already fully initialized by ``importlib.import_module`` inside
    ``create_module``.
    """

    def __init__(self, flowos_name: str, flowos_core_name: str) -> None:
        self.flowos_name = flowos_name
        self.flowos_core_name = flowos_core_name

    def create_module(self, spec):  # noqa: ARG002 - protocol signature
        return importlib.import_module(self.flowos_core_name)

    def exec_module(self, module):  # noqa: ARG002 - module already initialised
        return None


class _FlowOSComponentsAliasFinder(importlib.abc.MetaPathFinder):
    """Bridge ``flowos.components.<rest>`` -> ``flowos_core.components.<rest>`` for arbitrary subpackages.

    Replaces a stack of per-subpackage physical shim files with a single
    dynamic resolver, so a new flowos_core component module never requires a
    parallel flowos shim.  Saved flows that imported components via
    the legacy ``flowos.components.*`` paths (and the integration tests
    that document the contract) continue to load without modification.
    """

    _BRIDGE_PREFIX = "flowos.components"
    _FLOWOS_PREFIX = "flowos_core.components"

    # First-segment renames applied when translating ``flowos.components.<head>[.<tail>]``
    # to ``flowos_core.components.<renamed>[.<tail>]``.  ``knowledge_bases`` was
    # renamed to ``files_and_knowledge`` in flowos_core during the move; the
    # flowos-side import path stays as ``knowledge_bases`` so the
    # already-shipped saved flows continue to resolve.
    _PACKAGE_OVERRIDES = {
        "knowledge_bases": "files_and_knowledge",
    }

    def find_spec(self, fullname, path=None, target=None):  # noqa: ARG002 - protocol signature
        if fullname != self._BRIDGE_PREFIX and not fullname.startswith(self._BRIDGE_PREFIX + "."):
            return None
        rel = fullname[len(self._BRIDGE_PREFIX) :].lstrip(".")
        if rel:
            head, _, tail = rel.partition(".")
            head = self._PACKAGE_OVERRIDES.get(head, head)
            flowos_core_name = f"{self._FLOWOS_PREFIX}.{head}" + (f".{tail}" if tail else "")
        else:
            flowos_core_name = self._FLOWOS_PREFIX
        try:
            flowos_core_spec = importlib.util.find_spec(flowos_core_name)
        except (ImportError, ValueError, ModuleNotFoundError, AttributeError):
            return None
        if flowos_core_spec is None:
            return None
        # Mirror the flowos_core target's package-ness so ``__path__`` is set
        # correctly on the alias and downstream ``import`` statements that
        # treat the alias as a package keep working.
        is_package = flowos_core_spec.submodule_search_locations is not None
        return importlib.machinery.ModuleSpec(
            fullname,
            _FlowOSComponentsAliasLoader(fullname, flowos_core_name),
            is_package=is_package,
        )


class FlowOSCompatibilityModule(ModuleType):
    """A module that forwards attribute access to the corresponding flowos_core module."""

    def __init__(self, name: str, flowos_core_module_name: str):
        super().__init__(name)
        self._flowos_core_module_name = flowos_core_module_name
        self._flowos_core_module = None

    def _get_flowos_core_module(self):
        """Lazily import and cache the flowos_core module."""
        if self._flowos_core_module is None:
            try:
                self._flowos_core_module = importlib.import_module(self._flowos_core_module_name)
            except ImportError as e:
                msg = f"Cannot import {self._flowos_core_module_name} for backwards compatibility with {self.__name__}"
                raise ImportError(msg) from e
        return self._flowos_core_module

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the flowos_core module with caching."""
        flowos_core_module = self._get_flowos_core_module()
        try:
            attr = getattr(flowos_core_module, name)
        except AttributeError as e:
            msg = f"module '{self.__name__}' has no attribute '{name}'"
            raise AttributeError(msg) from e
        else:
            # Cache the attribute in our __dict__ for faster subsequent access
            setattr(self, name, attr)
            return attr

    def __dir__(self):
        """Return directory of the flowos_core module."""
        try:
            flowos_core_module = self._get_flowos_core_module()
            return dir(flowos_core_module)
        except ImportError:
            return []


def _setup_compatibility_modules():
    """Set up comprehensive compatibility modules for flowos.base imports."""
    # First, set up the base attribute on this module (flowos)
    current_module = sys.modules[__name__]

    # Install the dynamic ``flowos.components.<rest>`` -> ``flowos_core.components.<rest>``
    # bridge BEFORE any explicit module_mappings entries are registered.  The
    # finder handles every subpackage (including ones added later when a new
    # bundle is extracted), so the explicit per-helper entries that used to
    # live in module_mappings are no longer needed here.
    if not any(isinstance(f, _FlowOSComponentsAliasFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _FlowOSComponentsAliasFinder())

    # Define all the modules we need to support
    module_mappings = {
        # Core base module
        "flowos.base": "flowos_core.base",
        # Inputs module - critical for class identity
        "flowos.inputs": "flowos_core.inputs",
        "flowos.inputs.inputs": "flowos_core.inputs.inputs",
        # Schema modules - also critical for class identity
        "flowos.schema": "flowos_core.schema",
        "flowos.schema.data": "flowos_core.schema.data",
        "flowos.schema.serialize": "flowos_core.schema.serialize",
        # Template modules
        "flowos.template": "flowos_core.template",
        "flowos.template.field": "flowos_core.template.field",
        "flowos.template.field.base": "flowos_core.template.field.base",
        # ``flowos.components.*`` is bridged dynamically by
        # ``_FlowOSComponentsAliasFinder`` registered above, so no
        # entries are needed here.
        # Individual modules that exist in flowos_core
        "flowos.base.agents": "flowos_core.base.agents",
        "flowos.base.chains": "flowos_core.base.chains",
        "flowos.base.data": "flowos_core.base.data",
        "flowos.base.data.utils": "flowos_core.base.data.utils",
        "flowos.base.document_transformers": "flowos_core.base.document_transformers",
        "flowos.base.embeddings": "flowos_core.base.embeddings",
        "flowos.base.flow_processing": "flowos_core.base.flow_processing",
        "flowos.base.io": "flowos_core.base.io",
        "flowos.base.io.chat": "flowos_core.base.io.chat",
        "flowos.base.io.text": "flowos_core.base.io.text",
        "flowos.base.langchain_utilities": "flowos_core.base.langchain_utilities",
        "flowos.base.memory": "flowos_core.base.memory",
        "flowos.base.models": "flowos_core.base.models",
        "flowos.base.models.google_generative_ai_constants": "flowos_core.base.models.google_generative_ai_constants",
        "flowos.base.models.openai_constants": "flowos_core.base.models.openai_constants",
        "flowos.base.models.anthropic_constants": "flowos_core.base.models.anthropic_constants",
        "flowos.base.models.aiml_constants": "flowos_core.base.models.aiml_constants",
        "flowos.base.models.aws_constants": "flowos_core.base.models.aws_constants",
        "flowos.base.models.groq_constants": "flowos_core.base.models.groq_constants",
        "flowos.base.models.novita_constants": "flowos_core.base.models.novita_constants",
        "flowos.base.models.ollama_constants": "flowos_core.base.models.ollama_constants",
        "flowos.base.models.sambanova_constants": "flowos_core.base.models.sambanova_constants",
        "flowos.base.models.cometapi_constants": "flowos_core.base.models.cometapi_constants",
        "flowos.base.prompts": "flowos_core.base.prompts",
        "flowos.base.prompts.api_utils": "flowos_core.base.prompts.api_utils",
        "flowos.base.prompts.utils": "flowos_core.base.prompts.utils",
        "flowos.base.textsplitters": "flowos_core.base.textsplitters",
        "flowos.base.tools": "flowos_core.base.tools",
        "flowos.base.vectorstores": "flowos_core.base.vectorstores",
    }

    # Create compatibility modules for each mapping
    for flowos_name, flowos_core_name in module_mappings.items():
        if flowos_name not in sys.modules:
            # Check if the flowos_core module exists
            try:
                spec = importlib.util.find_spec(flowos_core_name)
                if spec is not None:
                    # Create compatibility module
                    compat_module = FlowOSCompatibilityModule(flowos_name, flowos_core_name)
                    sys.modules[flowos_name] = compat_module

                    # Set up the module hierarchy
                    parts = flowos_name.split(".")
                    if len(parts) > 1:
                        parent_name = ".".join(parts[:-1])
                        parent_module = sys.modules.get(parent_name)
                        if parent_module is not None:
                            setattr(parent_module, parts[-1], compat_module)

                    # Special handling for top-level modules
                    if flowos_name == "flowos.base":
                        current_module.base = compat_module
                    elif flowos_name == "flowos.inputs":
                        current_module.inputs = compat_module
                    elif flowos_name == "flowos.schema":
                        current_module.schema = compat_module
                    elif flowos_name == "flowos.template":
                        current_module.template = compat_module
                    elif flowos_name == "flowos.components":
                        current_module.components = compat_module
            except (ImportError, ValueError):
                # Skip modules that don't exist in flowos_core
                continue

    # Handle modules that exist only in flowos (like knowledge_bases)
    # These need special handling because they're not in flowos_core yet.
    # ``flowos.components.knowledge_bases`` is no longer listed here:
    # ``_FlowOSComponentsAliasFinder`` rewrites it to
    # ``flowos_core.components.files_and_knowledge`` via the override map and the
    # physical shim file used to live under ``components/knowledge_bases/``
    # has been removed.
    flowos_only_modules = {
        "flowos.base.data.kb_utils": "flowos.base.data.kb_utils",
        "flowos.base.knowledge_bases": "flowos.base.knowledge_bases",
    }

    for flowos_name in flowos_only_modules:
        if flowos_name not in sys.modules:
            try:
                # Try to find the actual physical module file
                from pathlib import Path

                base_dir = Path(__file__).parent

                if flowos_name == "flowos.base.data.kb_utils":
                    kb_utils_file = base_dir / "base" / "data" / "kb_utils.py"
                    if kb_utils_file.exists():
                        spec = importlib.util.spec_from_file_location(flowos_name, kb_utils_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[flowos_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("flowos.base.data")
                            if parent_module is not None:
                                parent_module.kb_utils = module

                elif flowos_name == "flowos.base.knowledge_bases":
                    kb_dir = base_dir / "base" / "knowledge_bases"
                    kb_init_file = kb_dir / "__init__.py"
                    if kb_init_file.exists():
                        spec = importlib.util.spec_from_file_location(flowos_name, kb_init_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[flowos_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("flowos.base")
                            if parent_module is not None:
                                parent_module.knowledge_bases = module

            except (ImportError, AttributeError):
                # If direct file loading fails, skip silently
                continue


# Set up all the compatibility modules
_setup_compatibility_modules()
