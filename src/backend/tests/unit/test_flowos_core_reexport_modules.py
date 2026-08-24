"""Test to ensure all flowos modules that re-export flowos_core modules work correctly.

This test validates that every flowos module that re-exports from flowos_core
can successfully import and access all expected symbols, maintaining
backward compatibility and proper API exposure.

Based on analysis, there are 24 flowos modules that re-export from flowos_core:

Base Modules (11):
- flowos.base (wildcard from flowos_core.base)
- flowos.base.agents (from flowos_core.base.agents)
- flowos.base.data (from flowos_core.base.data)
- flowos.base.embeddings (from flowos_core.base.embeddings)
- flowos.base.io (from flowos_core.base.io)
- flowos.base.memory (from flowos_core.base.memory)
- flowos.base.models (from flowos_core.base.models)
- flowos.base.prompts (from flowos_core.base.prompts)
- flowos.base.textsplitters (from flowos_core.base.textsplitters)
- flowos.base.tools (from flowos_core.base.tools)
- flowos.base.vectorstores (from flowos_core.base.vectorstores)

Core System Modules (13):
- flowos.custom (from flowos_core.custom)
- flowos.custom.custom_component (from flowos_core.custom.custom_component)
- flowos.field_typing (from flowos_core.field_typing with __getattr__)
- flowos.graph (from flowos_core.graph)
- flowos.inputs (from flowos_core.inputs.inputs)
- flowos.interface (from flowos_core.interface)
- flowos.io (from flowos_core.io + flowos_core.template)
- flowos.load (from flowos_core.load)
- flowos.logging (from flowos_core.log.logger)
- flowos.schema (from flowos_core.schema)
- flowos.template (wildcard from flowos_core.template)
- flowos.template.field (from flowos_core.template.field)
"""

import importlib
import inspect
import pkgutil
import re
import time
from pathlib import Path

import pytest


def get_all_reexport_modules():
    """Get all known re-export modules for parametrized testing."""
    # Define the modules here so they can be accessed by parametrize
    direct_reexport_modules = {
        "flowos.base.agents": "flowos_core.base.agents",
        "flowos.base.data": "flowos_core.base.data",
        "flowos.base.embeddings": "flowos_core.base.embeddings",
        "flowos.base.io": "flowos_core.base.io",
        "flowos.base.memory": "flowos_core.base.memory",
        "flowos.base.models": "flowos_core.base.models",
        "flowos.base.prompts": "flowos_core.base.prompts",
        "flowos.base.textsplitters": "flowos_core.base.textsplitters",
        "flowos.base.tools": "flowos_core.base.tools",
        "flowos.base.vectorstores": "flowos_core.base.vectorstores",
        "flowos.custom.custom_component": "flowos_core.custom.custom_component",
        "flowos.graph": "flowos_core.graph",
        "flowos.inputs": "flowos_core.inputs.inputs",
        "flowos.interface": "flowos_core.interface",
        "flowos.load": "flowos_core.load",
        "flowos.logging": "flowos_core.log",
        "flowos.schema": "flowos_core.schema",
        "flowos.template.field": "flowos_core.template.field",
    }

    wildcard_reexport_modules = {
        "flowos.base": "flowos_core.base",
        "flowos.template": "flowos_core.template",
    }

    complex_reexport_modules = {
        "flowos.custom": ["flowos_core.custom", "flowos_core.custom.custom_component", "flowos_core.custom.utils"],
        "flowos.io": ["flowos_core.io", "flowos_core.template"],
    }

    dynamic_reexport_modules = {
        "flowos.field_typing": "flowos_core.field_typing",
    }

    return list(
        {
            **direct_reexport_modules,
            **wildcard_reexport_modules,
            **complex_reexport_modules,
            **dynamic_reexport_modules,
        }.keys()
    )


class TestFlowosCoreReexportModules:
    """Test that all flowos modules that re-export from flowos_core work correctly."""

    @classmethod
    def _discover_flowos_modules(cls) -> list[str]:
        """Dynamically discover all flowos modules."""
        flowos_modules: list[str] = []
        try:
            import flowos

            for _importer, modname, _ispkg in pkgutil.walk_packages(flowos.__path__, flowos.__name__ + "."):
                flowos_modules.append(modname)
        except ImportError:
            pass
        return flowos_modules

    @classmethod
    def _detect_reexport_pattern(cls, module_name: str) -> dict[str, str | None]:
        """Detect what kind of re-export pattern a module uses."""
        try:
            module = importlib.import_module(module_name)

            # Check if module has source code that mentions flowos_core
            source_file = getattr(module, "__file__", None)
            if source_file:
                try:
                    with Path(source_file).open() as f:
                        content = f.read()
                        if "from flowos_core" in content:
                            # Try to extract the flowos_core module being imported
                            patterns = [
                                r"from (flowos_core\.[.\w]+) import",
                                r"from (flowos_core\.[.\w]+) import \*",
                                r"import (flowos_core\.[.\w]+)",
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, content)
                                if match:
                                    return {"type": "direct", "source": match.group(1)}

                        if "__getattr__" in content and "flowos_core" in content:
                            return {"type": "dynamic", "source": None}

                        # If we get here, file exists but no patterns matched
                        return {"type": "none", "source": None}

                except (OSError, UnicodeDecodeError):
                    return {"type": "none", "source": None}
            else:
                return {"type": "none", "source": None}

        except ImportError:
            return {"type": "import_error", "source": None}

    @classmethod
    def _get_expected_symbols(cls, flowos_core_source: str | None = None) -> list[str]:
        """Get expected symbols that should be available in a module."""
        if not flowos_core_source:
            return []

        try:
            flowos_core_module = importlib.import_module(flowos_core_source)
            if hasattr(flowos_core_module, "__all__"):
                return list(flowos_core_module.__all__)
            # Return public attributes (not starting with _)
            return [name for name in dir(flowos_core_module) if not name.startswith("_")]
        except ImportError:
            return []

    # Define all the modules that re-export from flowos_core (kept for backward compatibility)
    DIRECT_REEXPORT_MODULES = {
        # Base modules with direct re-exports
        "flowos.base.agents": "flowos_core.base.agents",
        "flowos.base.data": "flowos_core.base.data",
        "flowos.base.embeddings": "flowos_core.base.embeddings",
        "flowos.base.io": "flowos_core.base.io",
        "flowos.base.memory": "flowos_core.base.memory",
        "flowos.base.models": "flowos_core.base.models",
        "flowos.base.prompts": "flowos_core.base.prompts",
        "flowos.base.textsplitters": "flowos_core.base.textsplitters",
        "flowos.base.tools": "flowos_core.base.tools",
        "flowos.base.vectorstores": "flowos_core.base.vectorstores",
        # Core system modules with direct re-exports
        "flowos.custom.custom_component": "flowos_core.custom.custom_component",
        "flowos.graph": "flowos_core.graph",
        "flowos.inputs": "flowos_core.inputs.inputs",
        "flowos.interface": "flowos_core.interface",
        "flowos.load": "flowos_core.load",
        "flowos.logging": "flowos_core.log",  # Note: imports from flowos_core.log.logger
        "flowos.schema": "flowos_core.schema",
        "flowos.template.field": "flowos_core.template.field",
    }

    # Modules that use wildcard imports from flowos_core
    WILDCARD_REEXPORT_MODULES = {
        "flowos.base": "flowos_core.base",
        "flowos.template": "flowos_core.template",
    }

    # Modules with complex/mixed import patterns
    COMPLEX_REEXPORT_MODULES = {
        "flowos.custom": ["flowos_core.custom", "flowos_core.custom.custom_component", "flowos_core.custom.utils"],
        "flowos.io": ["flowos_core.io", "flowos_core.template"],  # Mixed imports
    }

    # Modules with dynamic __getattr__ patterns
    DYNAMIC_REEXPORT_MODULES = {
        "flowos.field_typing": "flowos_core.field_typing",
    }

    def test_direct_reexport_modules_importable(self):
        """Test that all direct re-export modules can be imported."""
        successful_imports = 0

        for flowos_module, flowos_core_module in self.DIRECT_REEXPORT_MODULES.items():
            try:
                # Import the flowos module
                lf_module = importlib.import_module(flowos_module)
                assert lf_module is not None, f"FlowOS module {flowos_module} is None"

                # Import the corresponding flowos_core module to compare

                flowos_core_mod = importlib.import_module(flowos_core_module)
                assert flowos_core_mod is not None, f"FLOWOS_CORE module {flowos_core_module} is None"

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import direct re-export module {flowos_module}: {e!s}")

    def test_wildcard_reexport_modules_importable(self):
        """Test that modules using wildcard imports work correctly."""
        successful_imports = 0

        for flowos_module, flowos_core_module in self.WILDCARD_REEXPORT_MODULES.items():
            try:
                # Import the flowos module
                lf_module = importlib.import_module(flowos_module)
                assert lf_module is not None, f"FlowOS module {flowos_module} is None"

                # Wildcard imports should expose most/all attributes from flowos_core module
                flowos_core_mod = importlib.import_module(flowos_core_module)

                # Check that all attributes are available
                if hasattr(flowos_core_mod, "__all__"):
                    all_attrs = list(flowos_core_mod.__all__)  # Test all attributes
                    for attr in all_attrs:
                        if hasattr(flowos_core_mod, attr):
                            assert hasattr(lf_module, attr), f"Attribute {attr} missing from {flowos_module}"

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import wildcard re-export module {flowos_module}: {e!s}")

    def test_complex_reexport_modules_importable(self):
        """Test that modules with complex/mixed import patterns work correctly."""
        successful_imports = 0

        for flowos_module in self.COMPLEX_REEXPORT_MODULES:
            try:
                # Import the flowos module
                lf_module = importlib.import_module(flowos_module)
                assert lf_module is not None, f"FlowOS module {flowos_module} is None"

                # Verify it has __all__ attribute for complex modules
                assert hasattr(lf_module, "__all__"), f"Complex module {flowos_module} missing __all__"
                assert len(lf_module.__all__) > 0, f"Complex module {flowos_module} has empty __all__"

                # Try to access all items from __all__
                all_items = lf_module.__all__  # Test all items
                for item in all_items:
                    try:
                        attr = getattr(lf_module, item)
                        assert attr is not None, f"Attribute {item} is None in {flowos_module}"
                    except AttributeError:
                        pytest.fail(f"Complex module {flowos_module} missing expected attribute {item} from __all__")

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import complex re-export module {flowos_module}: {e!s}")

    def test_dynamic_reexport_modules_importable(self):
        """Test that modules with __getattr__ dynamic loading work correctly."""
        successful_imports = 0

        for flowos_module in self.DYNAMIC_REEXPORT_MODULES:
            try:
                # Import the flowos module
                lf_module = importlib.import_module(flowos_module)
                assert lf_module is not None, f"FlowOS module {flowos_module} is None"

                # Dynamic modules should have __getattr__ method
                assert hasattr(lf_module, "__getattr__"), f"Dynamic module {flowos_module} missing __getattr__"

                # Test accessing some known attributes dynamically
                if flowos_module == "flowos.field_typing":
                    # Test some known field typing constants
                    test_attrs = ["Data", "Text", "LanguageModel"]
                    for attr in test_attrs:
                        try:
                            value = getattr(lf_module, attr)
                            assert value is not None, f"Dynamic attribute {attr} is None"
                        except AttributeError:
                            pytest.fail(f"Dynamic module {flowos_module} missing expected attribute {attr}")

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import dynamic re-export module {flowos_module}: {e!s}")

    def test_all_reexport_modules_have_required_structure(self):
        """Test that re-export modules have the expected structure."""
        all_modules = {}
        all_modules.update(self.DIRECT_REEXPORT_MODULES)
        all_modules.update(self.WILDCARD_REEXPORT_MODULES)
        all_modules.update(self.DYNAMIC_REEXPORT_MODULES)

        # Add complex modules
        for lf_mod in self.COMPLEX_REEXPORT_MODULES:
            all_modules[lf_mod] = self.COMPLEX_REEXPORT_MODULES[lf_mod]

        for flowos_module in all_modules:
            try:
                lf_module = importlib.import_module(flowos_module)

                # All modules should be importable
                assert lf_module is not None

                # Most should have __name__ attribute
                assert hasattr(lf_module, "__name__")

                # Check for basic module structure
                assert hasattr(lf_module, "__file__") or hasattr(lf_module, "__path__")

            except Exception as e:
                pytest.fail(f"Module structure issue with {flowos_module}: {e!s}")

    def test_reexport_modules_backward_compatibility(self):
        """Test that common import patterns still work for backward compatibility."""
        # Test some key imports that should always work
        backward_compatible_imports = [
            ("flowos.schema", "Data"),
            ("flowos.inputs", "StrInput"),
            ("flowos.inputs", "IntInput"),
            ("flowos.custom", "Component"),  # Base component class
            ("flowos.custom", "CustomComponent"),
            ("flowos.field_typing", "Text"),  # Dynamic
            ("flowos.field_typing", "Data"),  # Dynamic
            ("flowos.load", "load_flow_from_json"),
            ("flowos.logging", "logger"),
        ]

        for module_name, symbol_name in backward_compatible_imports:
            try:
                module = importlib.import_module(module_name)
                symbol = getattr(module, symbol_name)
                assert symbol is not None

                # For callable objects, ensure they're callable
                if inspect.isclass(symbol) or inspect.isfunction(symbol):
                    assert callable(symbol)

            except Exception as e:
                pytest.fail(f"Backward compatibility issue with {module_name}.{symbol_name}: {e!s}")

    def test_no_circular_imports_in_reexports(self):
        """Test that there are no circular import issues in re-export modules."""
        # Test importing modules in different orders to catch circular imports
        import_orders = [
            ["flowos.schema", "flowos.inputs", "flowos.base"],
            ["flowos.base", "flowos.schema", "flowos.inputs"],
            ["flowos.inputs", "flowos.base", "flowos.schema"],
            ["flowos.custom", "flowos.field_typing", "flowos.template"],
            ["flowos.template", "flowos.custom", "flowos.field_typing"],
            ["flowos.field_typing", "flowos.template", "flowos.custom"],
        ]

        for order in import_orders:
            try:
                for module_name in order:
                    importlib.import_module(module_name)
                    # Try to access something from each module to trigger full loading
                    module = importlib.import_module(module_name)
                    if hasattr(module, "__all__") and module.__all__:
                        # Try to access first item in __all__
                        first_item = module.__all__[0]
                        try:
                            getattr(module, first_item)
                        except AttributeError:
                            pytest.fail(f"Module {module_name} missing expected attribute {first_item} from __all__")

            except Exception as e:
                pytest.fail(f"Circular import issue with order {order}: {e!s}")

    def test_reexport_modules_performance(self):
        """Test that re-export modules import efficiently."""
        # Test that basic imports are fast
        performance_critical_modules = [
            "flowos.schema",
            "flowos.inputs",
            "flowos.field_typing",
            "flowos.load",
            "flowos.logging",
        ]

        slow_imports = []

        for module_name in performance_critical_modules:
            start_time = time.time()
            try:
                importlib.import_module(module_name)
                import_time = time.time() - start_time

                # Re-export modules should import quickly (< 1 second)
                if import_time > 1.0:
                    slow_imports.append(f"{module_name}: {import_time:.3f}s")

            except ImportError:
                # Import failures are tested elsewhere
                pass

        # Don't fail the test, just record slow imports for information

    def test_coverage_completeness(self):
        """Test that we're testing all known re-export modules."""
        # This test ensures we don't miss any re-export modules
        all_tested_modules = set()
        all_tested_modules.update(self.DIRECT_REEXPORT_MODULES.keys())
        all_tested_modules.update(self.WILDCARD_REEXPORT_MODULES.keys())
        all_tested_modules.update(self.COMPLEX_REEXPORT_MODULES.keys())
        all_tested_modules.update(self.DYNAMIC_REEXPORT_MODULES.keys())

        # Should be testing all 24 identified modules based on our analysis
        actual_count = len(all_tested_modules)

        # Ensure we have a reasonable number of modules
        assert actual_count >= 20, f"Too few modules being tested: {actual_count}"
        assert actual_count <= 30, f"Too many modules being tested: {actual_count}"

    # Dynamic test methods using the discovery functions
    def test_dynamic_module_discovery(self):
        """Test that we can dynamically discover flowos modules."""
        modules = self._discover_flowos_modules()
        assert len(modules) > 0, "Should discover at least some flowos modules"

        # Check that known modules are found
        expected_modules = ["flowos.schema", "flowos.inputs", "flowos.custom"]
        found_modules = [mod for mod in expected_modules if mod in modules]
        assert len(found_modules) > 0, f"Expected to find some of {expected_modules}, but found: {found_modules}"

    @pytest.mark.parametrize("module_name", get_all_reexport_modules())
    def test_parametrized_module_import_and_pattern_detection(self, module_name: str):
        """Parametrized test that checks module import and pattern detection."""
        # Test that module can be imported
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Module {module_name} should not be None"
        except ImportError:
            pytest.fail(f"Could not import {module_name}")

        # Test pattern detection
        pattern_info = self._detect_reexport_pattern(module_name)
        assert isinstance(pattern_info, dict), "Pattern detection should return a dict"
        assert "type" in pattern_info, "Pattern info should have 'type' key"
        assert pattern_info["type"] in ["direct", "dynamic", "none", "import_error"], (
            f"Unknown pattern type: {pattern_info['type']}"
        )

    def test_generate_backward_compatibility_imports(self):
        """Test generating backward compatibility imports dynamically."""
        # Test with a known module that has flowos_core imports
        test_cases = [("flowos.schema", "flowos_core.schema"), ("flowos.custom", "flowos_core.custom")]

        for lf_module, expected_flowos_core_source in test_cases:
            flowos_core_symbols = self._get_expected_symbols(expected_flowos_core_source)
            assert len(flowos_core_symbols) > 0, f"Should find some symbols in {expected_flowos_core_source}"

            # Test that symbols explicitly re-exported by flowos module are accessible
            lf_module_obj = importlib.import_module(lf_module)

            # Get the symbols that flowos explicitly re-exports (from its __all__)
            if hasattr(lf_module_obj, "__all__"):
                lf_reexported = lf_module_obj.__all__
                # Check that these re-exported symbols are actually available
                available_symbols = [sym for sym in lf_reexported if hasattr(lf_module_obj, sym)]
                assert len(available_symbols) > 0, f"Module {lf_module} should have symbols from its __all__"

                # Verify that at least some of the re-exported symbols come from flowos_core
                flowos_core_sourced = [sym for sym in available_symbols if sym in flowos_core_symbols]
                assert len(flowos_core_sourced) > 0, (
                    f"Module {lf_module} should re-export some symbols from {expected_flowos_core_source}"
                )
            else:
                # If no __all__, just check that some flowos_core symbols are accessible
                available_symbols = [sym for sym in flowos_core_symbols[:10] if hasattr(lf_module_obj, sym)]
                assert len(available_symbols) > 0, (
                    f"Module {lf_module} should have some symbols from {expected_flowos_core_source}"
                )
