from random import randint

from flowos_core.custom import Component
from flowos_core.inputs.inputs import IntInput, MessageTextInput
from flowos_core.template.field.base import Output


class MultipleOutputsComponent(Component):
    inputs = [
        MessageTextInput(display_name="Input", name="input"),
        IntInput(display_name="Number", name="number"),
    ]
    outputs = [
        Output(display_name="Certain Output", name="certain_output", method="certain_output"),
        Output(display_name="Other Output", name="other_output", method="other_output"),
    ]

    def certain_output(self) -> int:
        return randint(0, self.number)  # noqa: S311

    def other_output(self) -> int:
        return self.certain_output()
