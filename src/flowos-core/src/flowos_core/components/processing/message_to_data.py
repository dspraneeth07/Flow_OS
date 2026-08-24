from flowos_core.custom.custom_component.component import Component
from flowos_core.io import MessageInput, Output
from flowos_core.log.logger import logger
from flowos_core.schema.data import Data


class MessageToDataComponent(Component):
    display_name = "Message to Data"
    description = "Convert a Message object to a Data object"
    icon = "message-square-share"
    beta = True
    name = "MessagetoData"
    legacy = True
    replacement = ["processing.TypeConverterComponent"]

    inputs = [
        MessageInput(
            name="message",
            display_name="Message",
            info="The Message object to convert to a Data object",
        ),
    ]

    outputs = [
        Output(display_name="JSON", name="data", method="convert_message_to_data"),
    ]

    def convert_message_to_data(self) -> Data:
        # Check for Message by checking if it has the expected attributes instead of isinstance
        if hasattr(self.message, "data") and hasattr(self.message, "text") and hasattr(self.message, "get_text"):
            # Convert Message to Data - this works for both flowos.Message and flowos_core.Message
            return Data(data=self.message.data)

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.debug(msg, exc_info=True)
        self.status = msg
        return Data(data={"error": msg})
