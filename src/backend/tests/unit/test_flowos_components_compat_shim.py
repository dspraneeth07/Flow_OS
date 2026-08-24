"""Tests for the dynamic ``flowos.components.*`` -> ``flowos_core.components.*`` bridge.

Saved flows in the wild import their components via the legacy
``flowos.components.<sub>.<leaf>`` paths (the integration test
``test_dynamic_import_integration.py`` documents this contract).  The
flowos_core extraction moved every component module into ``flowos_core.components.*``;
``flowos/__init__.py`` installs a meta path finder that bridges the
two namespaces dynamically so saved flows keep loading without
modification.

This suite locks the contract:

    1. Generic prefix bridge: ``flowos.components.<rest>`` resolves to
       ``flowos_core.components.<rest>`` for arbitrary subpackages and submodules,
       including new bundles extracted in the future.
    2. Renamed-package override: ``flowos.components.knowledge_bases``
       (and any submodule under it) resolves to
       ``flowos_core.components.files_and_knowledge`` because the package was
       renamed during the move while the flowos-side path stays for
       saved-flow compat.
    3. Class identity is preserved: a class loaded via the flowos path
       is the same object as the one loaded via the flowos_core path, so
       ``isinstance`` checks across the bridge keep working.
"""

from __future__ import annotations

import importlib
import sys

import flowos  # noqa: F401  -- triggers the meta finder install


def test_dotted_submodule_import_resolves() -> None:
    """``from flowos.components.processing.converter import X`` works.

    Regression: the deletion of the physical ``flowos/components/processing/converter.py``
    shim broke this import path before the dynamic bridge landed.
    """
    from flowos.components.processing.converter import convert_to_dataframe

    # The bridge is a name alias, not a copy; ``__module__`` reflects the
    # underlying flowos_core location so debuggers / stack traces point at the
    # canonical source file.
    assert convert_to_dataframe.__module__ == "flowos_core.components.processing.converter"


def test_helpers_subpackage_imports() -> None:
    """``from flowos.components.helpers import X`` works for any helper class."""
    from flowos.components.helpers import CalculatorComponent

    assert CalculatorComponent.__module__.startswith("flowos_core.components.")


def test_knowledge_bases_override_resolves_to_files_and_knowledge() -> None:
    """``flowos.components.knowledge_bases[.<rest>]`` -> ``flowos_core.components.files_and_knowledge[.<rest>]``.

    The flowos_core package was renamed during the move; the flowos-side path
    stays as ``knowledge_bases`` so saved flows that imported via that
    name continue to resolve.
    """
    from flowos.components.knowledge_bases.retrieval import KnowledgeBaseComponent

    assert KnowledgeBaseComponent.__module__ == "flowos_core.components.files_and_knowledge.retrieval"


def test_class_identity_preserved_across_bridge() -> None:
    """Same class is returned via ``flowos.components.X`` and ``flowos_core.components.X``.

    Critical for ``isinstance`` checks against types resolved through
    either path -- e.g. a saved flow imports the legacy flowos path
    while runtime code imports the flowos_core path; both must compare equal.
    """
    import flowos.components.processing.converter as flowos_module
    import flowos_core.components.processing.converter as flowos_core_module

    assert flowos_module is flowos_core_module
    assert flowos_module.convert_to_dataframe is flowos_core_module.convert_to_dataframe


def test_top_level_components_is_aliased_to_flowos_core_components() -> None:
    """``import flowos.components`` resolves to the flowos_core package.

    Catches the case where the meta finder isn't installed yet when
    ``flowos.components`` is first imported -- happens on cold imports
    in test runs that don't go through ``flowos.__init__`` first.
    """
    import flowos.components
    import flowos_core.components

    assert flowos.components is flowos_core.components


def test_arbitrary_extracted_bundle_resolves_via_dynamic_bridge() -> None:
    """A bundle that exists in flowos_core but had no physical ``flowos/components`` shim resolves.

    Regression-future: the previous shim layout required a parallel
    physical file per subpackage; forgetting to add one silently broke
    pre-existing flows.  The dynamic bridge means a new flowos_core component
    module is reachable via the legacy flowos path immediately.
    """
    # Pick any subpackage under flowos_core.components that didn't have a
    # physical shim under flowos/components/ before the deletion.
    target = "flowos_core.components.helpers.calculator_core"
    importlib.import_module(target)
    bridge = importlib.import_module("flowos.components.helpers.calculator_core")
    assert bridge is sys.modules[target]
