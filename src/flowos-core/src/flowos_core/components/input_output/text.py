from typing import Any

from flowos_core.base.io.text import TextComponent
from flowos_core.io import BoolInput, MultilineInput, Output
from flowos_core.schema.message import Message


class TextInputComponent(TextComponent):
    display_name = "Text Input"
    description = "Get user text inputs."
    documentation: str = "https://docs.flowos.org/text-input-and-output"
    icon = "type"
    name = "TextInput"
    legacy = True
    replacement = ["input_output.ChatInput"]

    inputs = [
        MultilineInput(
            name="input_value",
            display_name="Text",
            info="Text to be passed as input.",
        ),
        BoolInput(
            name="use_global_variable",
            display_name="Use Global Variable",
            info="Enable to select from global variables (shows globe icon). Disables multiline editing.",
            value=False,
            advanced=True,
            real_time_refresh=True,
        ),
    ]
    outputs = [
        Output(display_name="Output Text", name="text", method="text_response"),
    ]

    def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        if field_name == "use_global_variable":
            if field_value:
                # Enable global variable mode: single-line with password masking and globe dropdown
                build_config["input_value"]["multiline"] = False
                build_config["input_value"]["password"] = True
            else:
                # Default mode: multiline text editing
                build_config["input_value"]["multiline"] = True
                build_config["input_value"]["password"] = False
        return build_config

    def text_response(self) -> Message:
        return Message(
            text=self.input_value,
        )
