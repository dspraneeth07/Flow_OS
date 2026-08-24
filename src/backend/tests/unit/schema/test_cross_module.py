"""Unit tests for cross-module isinstance functionality.

These tests verify that isinstance checks work correctly when classes are
re-exported from different modules (e.g., flowos_core.schema.Message vs flowos.schema.Message).
"""

from flowos.schema import Data as FlowOSData
from flowos.schema import Message as FlowOSMessage
from flowos_core.schema.data import Data as FlowosCoreData
from flowos_core.schema.message import Message as FlowosCoreMessage


class TestDuckTypingData:
    """Tests for duck-typing Data class across module boundaries."""

    def test_flowos_core_data_isinstance_flowos_data(self):
        """Test that flowos_core.Data instance is recognized as flowos.Data."""
        flowos_core_data = FlowosCoreData(data={"key": "value"})
        assert isinstance(flowos_core_data, FlowOSData)

    def test_flowos_data_isinstance_flowos_core_data(self):
        """Test that flowos.Data instance is recognized as flowos_core.Data."""
        flowos_data = FlowOSData(data={"key": "value"})
        assert isinstance(flowos_data, FlowosCoreData)

    def test_data_equality_across_modules(self):
        """Test that Data objects from different modules are equal."""
        flowos_core_data = FlowosCoreData(data={"key": "value"})
        flowos_data = FlowOSData(data={"key": "value"})
        assert flowos_core_data == flowos_data

    def test_data_interchangeable_in_functions(self):
        """Test that Data from different modules work interchangeably."""

        def process_data(data: FlowOSData) -> str:
            return data.get_text()

        flowos_core_data = FlowosCoreData(data={"text": "hello"})
        # Should not raise type error
        result = process_data(flowos_core_data)
        assert result == "hello"

    def test_data_model_dump_compatible(self):
        """Test that model_dump works across module boundaries."""
        flowos_core_data = FlowosCoreData(data={"key": "value"})
        flowos_data = FlowOSData(**flowos_core_data.model_dump())
        assert flowos_data.data == {"key": "value"}


class TestDuckTypingMessage:
    """Tests for duck-typing Message class across module boundaries."""

    def test_flowos_core_message_isinstance_flowos_message(self):
        """Test that flowos_core.Message instance is recognized as flowos.Message."""
        flowos_core_message = FlowosCoreMessage(text="hello")
        assert isinstance(flowos_core_message, FlowOSMessage)

    def test_flowos_message_isinstance_flowos_core_message(self):
        """Test that flowos.Message instance is recognized as flowos_core.Message."""
        flowos_message = FlowOSMessage(text="hello")
        assert isinstance(flowos_message, FlowosCoreMessage)

    def test_message_equality_across_modules(self):
        """Test that Message objects from different modules are equal."""
        flowos_core_message = FlowosCoreMessage(text="hello", sender="user")
        flowos_message = FlowOSMessage(text="hello", sender="user")
        # Note: Direct equality might not work due to timestamps
        assert flowos_core_message.text == flowos_message.text
        assert flowos_core_message.sender == flowos_message.sender

    def test_message_interchangeable_in_functions(self):
        """Test that Message from different modules work interchangeably."""

        def process_message(msg: FlowOSMessage) -> str:
            return f"Processed: {msg.text}"

        flowos_core_message = FlowosCoreMessage(text="hello")
        # Should not raise type error
        result = process_message(flowos_core_message)
        assert result == "Processed: hello"

    def test_message_model_dump_compatible(self):
        """Test that model_dump works across module boundaries."""
        flowos_core_message = FlowosCoreMessage(text="hello", sender="user")
        dump = flowos_core_message.model_dump()
        flowos_message = FlowOSMessage(**dump)
        assert flowos_message.text == "hello"
        assert flowos_message.sender == "user"

    def test_message_inherits_data_duck_typing(self):
        """Test that Message inherits duck-typing from Data."""
        flowos_core_message = FlowosCoreMessage(text="hello")
        # Should work as Data too
        assert isinstance(flowos_core_message, FlowOSData)
        assert isinstance(flowos_core_message, FlowosCoreData)


class TestDuckTypingWithInputs:
    """Tests for duck-typing with input validation."""

    def test_message_input_accepts_flowos_core_message(self):
        """Test that MessageInput accepts flowos_core.Message."""
        from flowos_core.inputs.inputs import MessageInput

        flowos_core_message = FlowosCoreMessage(text="hello")
        msg_input = MessageInput(name="test", value=flowos_core_message)
        assert isinstance(msg_input.value, (FlowosCoreMessage, FlowOSMessage))

    def test_message_input_converts_cross_module(self):
        """Test that MessageInput handles cross-module Messages."""
        from flowos_core.inputs.inputs import MessageInput

        flowos_message = FlowOSMessage(text="hello")
        msg_input = MessageInput(name="test", value=flowos_message)
        # Should recognize it as a Message
        assert msg_input.value.text == "hello"

    def test_data_input_accepts_flowos_core_data(self):
        """Test that DataInput accepts flowos_core.Data."""
        from flowos_core.inputs.inputs import DataInput

        flowos_core_data = FlowosCoreData(data={"key": "value"})
        data_input = DataInput(name="test", value=flowos_core_data)
        assert data_input.value == flowos_core_data


class TestDuckTypingEdgeCases:
    """Tests for edge cases in cross-module isinstance checks."""

    def test_different_class_name_not_cross_module(self):
        """Test that objects with different class names are not recognized as cross-module compatible."""
        from flowos_core.schema.cross_module import CrossModuleModel

        class CustomModel(CrossModuleModel):
            value: str

        custom = CustomModel(value="test")
        # Should not be considered a Data
        assert not isinstance(custom, FlowosCoreData)
        assert not isinstance(custom, FlowOSData)

    def test_non_pydantic_model_not_cross_module(self):
        """Test that non-Pydantic objects are not recognized as cross-module compatible."""

        class FakeData:
            def __init__(self):
                self.data = {}

        fake = FakeData()
        assert not isinstance(fake, FlowosCoreData)
        assert not isinstance(fake, FlowOSData)

    def test_missing_fields_not_cross_module(self):
        """Test that objects missing required fields are not recognized as cross-module compatible."""
        from flowos_core.schema.cross_module import CrossModuleModel

        class PartialData(CrossModuleModel):
            text_key: str

        partial = PartialData(text_key="text")
        # Should not be considered a full Data (missing data field)
        assert not isinstance(partial, FlowosCoreData)
        assert not isinstance(partial, FlowOSData)


class TestDuckTypingInputMixin:
    """Tests for cross-module isinstance checks in BaseInputMixin and subclasses."""

    def test_base_input_mixin_is_cross_module(self):
        """Test that BaseInputMixin uses CrossModuleModel."""
        from flowos_core.inputs.input_mixin import BaseInputMixin
        from flowos_core.schema.cross_module import CrossModuleModel

        # Check that BaseInputMixin inherits from CrossModuleModel
        assert issubclass(BaseInputMixin, CrossModuleModel)

    def test_input_subclasses_inherit_cross_module(self):
        """Test that all input types inherit cross-module support."""
        from flowos_core.inputs.inputs import (
            BoolInput,
            DataInput,
            FloatInput,
            IntInput,
            MessageInput,
            StrInput,
        )
        from flowos_core.schema.cross_module import CrossModuleModel

        for input_class in [StrInput, IntInput, FloatInput, BoolInput, DataInput, MessageInput]:
            assert issubclass(input_class, CrossModuleModel)

    def test_input_instances_work_across_modules(self):
        """Test that input instances work with duck-typing."""
        from flowos_core.inputs.inputs import MessageInput

        # Create with flowos_core Message
        flowos_core_msg = FlowosCoreMessage(text="hello")
        input1 = MessageInput(name="test1", value=flowos_core_msg)

        # Create with flowos Message
        flowos_msg = FlowOSMessage(text="world")
        input2 = MessageInput(name="test2", value=flowos_msg)

        # Both should work
        assert input1.value.text == "hello"
        assert input2.value.text == "world"
