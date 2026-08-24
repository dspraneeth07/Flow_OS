from abc import abstractmethod
from collections.abc import Sequence

from flowos_core.custom.custom_component.component import Component
from flowos_core.field_typing import Tool
from flowos_core.io import Output
from flowos_core.schema.data import Data
from flowos_core.schema.dataframe import DataFrame


class LCToolComponent(Component):
    trace_type = "tool"
    outputs = [
        Output(name="api_run_model", display_name="JSON", method="run_model"),
        Output(name="api_build_tool", display_name="Tool", method="build_tool"),
    ]

    def _validate_outputs(self) -> None:
        required_output_methods = ["run_model", "build_tool"]
        output_names = [output.name for output in self.outputs]
        for method_name in required_output_methods:
            if method_name not in output_names:
                msg = f"Output with name '{method_name}' must be defined."
                raise ValueError(msg)
            if not hasattr(self, method_name):
                msg = f"Method '{method_name}' must be defined."
                raise ValueError(msg)

    @abstractmethod
    def run_model(self) -> Data | list[Data] | DataFrame:
        """Run model and return the output."""

    @abstractmethod
    def build_tool(self) -> Tool | Sequence[Tool]:
        """Build the tool."""
