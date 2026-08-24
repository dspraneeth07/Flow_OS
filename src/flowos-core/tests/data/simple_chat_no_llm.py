"""A simple chat flow example for FlowOS.

This script demonstrates how to set up a basic conversational flow using FlowOS's ChatInput and ChatOutput components.

Features:
- Configures logging to 'flowos.log' at INFO level
- Connects ChatInput to ChatOutput
- Builds a Graph object for the flow

Usage:
    python simple_chat.py

You can use this script as a template for building more complex conversational flows in FlowOS.
"""

from pathlib import Path

from flowos_core.components.input_output import ChatInput, ChatOutput
from flowos_core.graph import Graph
from flowos_core.log.logger import LogConfig

log_config = LogConfig(
    log_level="INFO",
    log_file=Path("flowos.log"),
)
chat_input = ChatInput()
chat_output = ChatOutput().set(input_value=chat_input.message_response)

graph = Graph(chat_input, chat_output, log_config=log_config)
