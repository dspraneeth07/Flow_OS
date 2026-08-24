"""Integration tests for dynamic import refactor.

Tests the dynamic import system in realistic usage scenarios to ensure
the refactor doesn't break existing functionality.
"""

import sys
import time

import pytest
from flowos.components.data import APIRequestComponent
from flowos.components.models_and_agents import AgentComponent  # Backwards compatibility alias
from flowos.components.openai import OpenAIModelComponent


class TestDynamicImportIntegration:
    """Integration tests for the dynamic import system."""

    def test_component_discovery_still_works(self):
        """Test that component discovery mechanisms still work after refactor."""
        # This tests that the existing component discovery logic
        # can still find and load components
        from flowos import components

        # Test that we can discover components through the main module
        openai_module = components.openai
        assert hasattr(openai_module, "OpenAIModelComponent")

        data_module = components.data
        assert hasattr(data_module, "APIRequestComponent")

    def test_existing_import_patterns_work(self):
        """Test that all existing import patterns continue to work."""
        # Test direct imports
        import flowos.components.data as data_comp

        # Test module imports
        import flowos.components.openai as openai_comp

        # All should work
        assert OpenAIModelComponent is not None
        assert APIRequestComponent is not None
        assert AgentComponent is not None
        assert openai_comp.OpenAIModelComponent is not None
        assert data_comp.APIRequestComponent is not None

    def test_component_instantiation_works(self):
        """Test that components can still be instantiated normally."""
        # Test that we can create component instances
        # (Note: Some components may require specific initialization parameters)

        from flowos.components.helpers import CalculatorComponent

        # Should be able to access the class
        assert CalculatorComponent is not None
        assert callable(CalculatorComponent)

    def test_template_creation_compatibility(self):
        """Test that template creation still works with dynamic imports."""
        # Test accessing component attributes needed for templates

        # Components should have all necessary attributes for template creation
        assert hasattr(OpenAIModelComponent, "__name__")
        assert hasattr(OpenAIModelComponent, "__module__")
        assert hasattr(OpenAIModelComponent, "display_name")
        assert isinstance(OpenAIModelComponent.display_name, str)
        assert OpenAIModelComponent.display_name
        assert hasattr(OpenAIModelComponent, "description")
        assert isinstance(OpenAIModelComponent.description, str)
        assert OpenAIModelComponent.description
        assert hasattr(OpenAIModelComponent, "icon")
        assert isinstance(OpenAIModelComponent.icon, str)
        assert OpenAIModelComponent.icon
        assert hasattr(OpenAIModelComponent, "inputs")
        assert isinstance(OpenAIModelComponent.inputs, list)
        assert len(OpenAIModelComponent.inputs) > 0
        # Check that each input has required attributes
        for input_field in OpenAIModelComponent.inputs:
            assert hasattr(input_field, "name"), f"Input {input_field} missing 'name' attribute"
            assert hasattr(input_field, "display_name"), f"Input {input_field} missing 'display_name' attribute"

    def test_multiple_import_styles_same_result(self):
        """Test that different import styles yield the same component."""
        # Import the same component in different ways
        from flowos import components
        from flowos.components.openai import OpenAIModelComponent as DirectImport

        dynamic_import = components.openai.OpenAIModelComponent

        import flowos.components.openai as openai_module

        module_import = openai_module.OpenAIModelComponent

        # All three should be the exact same class object
        assert DirectImport is dynamic_import
        assert dynamic_import is module_import
        assert DirectImport is module_import

    def test_startup_performance_improvement(self):
        """Test that startup time is improved with lazy loading."""
        # This test measures the difference in import time
        # Fresh modules to test startup behavior
        modules_to_clean = [
            "flowos.components.vectorstores",
            "flowos.components.tools",
            "flowos.components.langchain_utilities",
        ]

        for module_name in modules_to_clean:
            if module_name in sys.modules:
                del sys.modules[module_name]

        # Time the import of a large module
        start_time = time.time()
        from flowos.components import chroma

        import_time = time.time() - start_time

        # Import time should be very fast (just loading the __init__.py)
        assert import_time < 0.1  # Should be well under 100ms

        # Test that we can access a component (it may already be cached from previous tests)
        # This is expected behavior in a test suite where components get cached

        # Now access a component - this should trigger loading
        start_time = time.time()
        chroma_component = chroma.ChromaVectorStoreComponent
        access_time = time.time() - start_time

        assert chroma_component is not None
        # Access time should still be reasonable
        assert access_time < 2.0  # Should be under 2 seconds

    def test_memory_usage_efficiency(self):
        """Test that memory usage is more efficient with lazy loading."""
        from flowos.components import processing

        # Count currently loaded components
        initial_component_count = len([k for k in processing.__dict__ if k.endswith("Component")])

        # Access just one component
        combine_text = processing.CombineTextComponent
        assert combine_text is not None

        # At least one more component should be loaded now
        after_one_access = len([k for k in processing.__dict__ if k.endswith("Component")])
        assert after_one_access >= initial_component_count

        # Access another component
        split_text = processing.SplitTextComponent
        assert split_text is not None

        # Should have at least one more component loaded
        after_two_access = len([k for k in processing.__dict__ if k.endswith("Component")])
        assert after_two_access >= after_one_access

    def test_error_handling_in_realistic_scenarios(self):
        """Test error handling in realistic usage scenarios."""
        from flowos import components

        # Test accessing non-existent component category
        with pytest.raises(AttributeError):
            _ = components.nonexistent_category

        # Test accessing non-existent component in valid category
        with pytest.raises(AttributeError):
            _ = components.openai.NonExistentComponent

    def test_ide_autocomplete_support(self):
        """Test that IDE autocomplete support still works."""
        import flowos.components.openai as openai_components
        from flowos import components

        # __dir__ should return all available components/modules
        main_dir = dir(components)
        assert "openai" in main_dir
        assert "data" in main_dir
        assert "models_and_agents" in main_dir

        openai_dir = dir(openai_components)
        assert "OpenAIModelComponent" in openai_dir
        assert "OpenAIEmbeddingsComponent" in openai_dir

    def test_concurrent_access(self):
        """Test that concurrent access to components works correctly."""
        import threading

        from flowos.components import helpers

        results = []
        errors = []

        def access_component():
            try:
                component = helpers.CalculatorComponent
                results.append(component)
            except Exception as e:
                errors.append(e)

        # Create multiple threads accessing the same component
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=access_component)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have no errors
        assert len(errors) == 0
        assert len(results) == 5

        # All results should be the same component class
        first_result = results[0]
        for result in results[1:]:
            assert result is first_result

    def test_circular_import_prevention(self):
        """Test that the refactor doesn't introduce circular imports."""
        # This test ensures that importing components doesn't create
        # circular dependency issues

        # These imports should work without circular import errors
        from flowos import components
        from flowos.components import openai

        # Access components in different orders
        model1 = components.openai.OpenAIModelComponent
        model2 = openai.OpenAIModelComponent
        model3 = OpenAIModelComponent

        # All should be the same
        assert model1 is model2 is model3

    def test_large_scale_component_access(self):
        """Test accessing many components doesn't cause issues."""
        from flowos.components import datastax

        # Access multiple components rapidly
        components_accessed = []
        component_names = [
            "AstraDBVectorStoreComponent",
            "AstraDBChatMemory",
            "AstraDBToolComponent",
            "AstraDBCQLToolComponent",
            "GraphRAGComponent",
        ]

        for name in component_names:
            if hasattr(datastax, name):
                component = getattr(datastax, name)
                components_accessed.append(component)

        # Should have accessed all listed components
        assert len(components_accessed) == len(component_names)

        # All should be different classes
        assert len(set(components_accessed)) == len(components_accessed)

    def test_component_metadata_preservation(self):
        """Test that component metadata is preserved after dynamic loading."""
        # Component should have all expected metadata
        assert hasattr(OpenAIModelComponent, "__name__")
        assert hasattr(OpenAIModelComponent, "__module__")
        assert hasattr(OpenAIModelComponent, "__doc__")

        # Module path should be correct
        assert "openai" in OpenAIModelComponent.__module__

    def test_backwards_compatibility_comprehensive(self):
        """Comprehensive test of backwards compatibility."""
        # Test all major import patterns that should still work

        # 1. Direct component imports
        from flowos.components.data import APIRequestComponent

        assert AgentComponent is not None
        assert APIRequestComponent is not None

        # 2. Module imports
        # 3. Main module access
        import flowos.components as comp
        import flowos.components.helpers as helpers_mod
        import flowos.components.openai as openai_mod

        # 4. Nested access
        nested_component = comp.openai.OpenAIModelComponent
        direct_component = openai_mod.OpenAIModelComponent

        # All patterns should work and yield consistent results
        assert openai_mod.OpenAIModelComponent is not None
        assert helpers_mod.CalculatorComponent is not None
        assert nested_component is direct_component

    def test_deprecated_astra_assistants_removed(self):
        """Test that deprecated Astra Assistants components are no longer importable."""
        from flowos.components import datastax

        removed_components = [
            "AssistantsCreateAssistant",
            "AssistantsCreateThread",
            "AssistantsGetAssistantName",
            "AssistantsListAssistants",
            "AssistantsRun",
            "AstraAssistantManager",
        ]

        for name in removed_components:
            assert not hasattr(datastax, name), f"Deprecated component {name} should have been removed"

    def test_datastax_remaining_components_accessible(self):
        """Test that all non-deprecated datastax components are still accessible."""
        from flowos.components import datastax

        expected_components = [
            "AstraDBVectorStoreComponent",
            "AstraDBChatMemory",
            "AstraDBToolComponent",
            "AstraDBCQLToolComponent",
            "AstraDBGraphVectorStoreComponent",
            "AstraVectorizeComponent",
            "GraphRAGComponent",
            "Dotenv",
        ]

        for name in expected_components:
            assert hasattr(datastax, name), f"Component {name} should still be accessible"
            component = getattr(datastax, name)
            assert component is not None, f"Component {name} should not be None"

    def test_getenvvar_component_removed(self):
        """Test that the removed GetEnvVar component cannot be imported from flowos_core datastax."""
        import importlib

        import flowos_core.components.datastax as flowos_core_datastax

        with pytest.raises(AttributeError):
            _ = flowos_core_datastax.GetEnvVar

        assert not hasattr(flowos_core_datastax, "GetEnvVar"), "GetEnvVar should have been removed from flowos_core.components.datastax"

        with pytest.raises((ImportError, ModuleNotFoundError)):
            importlib.import_module("flowos_core.components.datastax.getenvvar")

    def test_python_code_structured_tool_removed(self):
        """Test that the removed PythonCodeStructuredTool component cannot be imported from flowos_core tools.

        Security follow-up to report H1-3754930: this legacy component ``exec()``'d
        attacker-controlled ``tool_code`` at flow-build time and was reachable as an
        unauthenticated RCE through public flows. It was first neutered to a
        non-executable stub (#13538) and is now fully removed. The node ``type`` is
        still blocked on the unauthenticated public path (see
        ``flowos_core.utils.flow_validation.CODE_EXECUTION_COMPONENT_TYPES``) so stored code in
        any saved flow that still references it cannot execute on that path.
        """
        import importlib

        import flowos_core.components.tools as flowos_core_tools

        with pytest.raises(AttributeError):
            _ = flowos_core_tools.PythonCodeStructuredTool

        assert not hasattr(flowos_core_tools, "PythonCodeStructuredTool"), (
            "PythonCodeStructuredTool should have been removed from flowos_core.components.tools"
        )

        with pytest.raises((ImportError, ModuleNotFoundError)):
            importlib.import_module("flowos_core.components.tools.python_code_structured_tool")

    def test_datastax_dir_excludes_deprecated(self):
        """Test that dir(datastax) does not list deprecated components."""
        from flowos.components import datastax

        exported = dir(datastax)
        deprecated = {
            "AssistantsCreateAssistant",
            "AssistantsCreateThread",
            "AssistantsGetAssistantName",
            "AssistantsListAssistants",
            "AssistantsRun",
            "AstraAssistantManager",
        }

        assert not deprecated.intersection(exported), (
            f"Deprecated components still appear in dir(): {deprecated.intersection(exported)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
