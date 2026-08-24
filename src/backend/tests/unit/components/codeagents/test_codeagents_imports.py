import importlib


def test_codeagents_bundle_exposed_via_components_package():
    components = importlib.import_module("flowos_core.components")
    assert hasattr(components, "codeagents"), "codeagents bundle should be discoverable"


def test_codeagents_components_lazy_import():
    codeagents = importlib.import_module("flowos_core.components.codeagents")
    # Ensure dynamic imports map includes both components
    assert hasattr(codeagents, "CodeActAgentSmolagentsComponent")
    assert hasattr(codeagents, "OpenDsStarAgentComponent")
