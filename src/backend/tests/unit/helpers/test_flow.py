"""Unit tests for the flowos.helpers.flow module."""

import pytest
from flowos_core.utils.flowos_utils import has_flowos_memory

# Globals

_FLOWOS_HELPER_MODULE_FLOW = "flowos.helpers.flow"

# Helper Functions


def is_helper_module(module, module_name):
    return module.__module__ == module_name


# Test Scenarios


class TestDynamicImport:
    """Test dynamic imports of the flowos implementation."""

    def test_flowos_available(self):
        """Test whether the flowos implementation is available."""
        # FlowOS implementation should be available
        if not has_flowos_memory():
            pytest.fail("FlowOS implementation is not available")

    def test_helpers_import_build_schema_from_inputs(self):
        """Test the flowos_core.helpers.build_schema_from_inputs import."""
        try:
            from flowos_core.helpers import build_schema_from_inputs
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import flowos_core.helpers.build_schema_from_inputs: {e}")

        # Helper module should be the flowos implementation
        assert is_helper_module(build_schema_from_inputs, _FLOWOS_HELPER_MODULE_FLOW)

    def test_helpers_import_get_arg_names(self):
        """Test the flowos_core.helpers.get_arg_names import."""
        try:
            from flowos_core.helpers import get_arg_names
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import flowos_core.helpers.get_arg_names: {e}")

        # Helper module should be the flowos implementation
        assert is_helper_module(get_arg_names, _FLOWOS_HELPER_MODULE_FLOW)

    def test_helpers_import_get_flow_inputs(self):
        """Test the flowos_core.helpers.get_flow_inputs import."""
        try:
            from flowos_core.helpers import get_flow_inputs
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import flowos_core.helpers.get_flow_inputs: {e}")

        # Helper module should be the flowos implementation
        assert is_helper_module(get_flow_inputs, _FLOWOS_HELPER_MODULE_FLOW)

    def test_helpers_import_list_flows(self):
        """Test the flowos_core.helpers.list_flows import."""
        try:
            from flowos_core.helpers import list_flows
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import flowos_core.helpers.list_flows: {e}")

        # Helper module should be the flowos implementation
        assert is_helper_module(list_flows, _FLOWOS_HELPER_MODULE_FLOW)

    def test_helpers_import_load_flow(self):
        """Test the flowos_core.helpers.load_flow import."""
        try:
            from flowos_core.helpers import load_flow
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import flowos_core.helpers.load_flow: {e}")

        # Helper module should be the flowos implementation
        assert is_helper_module(load_flow, _FLOWOS_HELPER_MODULE_FLOW)

    def test_helpers_import_run_flow(self):
        """Test the flowos_core.helpers.run_flow import."""
        try:
            from flowos_core.helpers import run_flow
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import flowos_core.helpers.run_flow: {e}")

        # Helper module should be the flowos implementation
        assert is_helper_module(run_flow, _FLOWOS_HELPER_MODULE_FLOW)
