"""Pure flow-building utilities for constructing FlowOS flows programmatically.

All functions operate on plain dicts — no I/O, no network, no global state.
"""

from flowos_core.graph.flow_builder.component import (
    add_component,
    configure_component,
    get_component,
    list_components,
    needs_server_update,
    remove_component,
)
from flowos_core.graph.flow_builder.connect import (
    add_connection,
    list_connections,
    remove_connection,
)
from flowos_core.graph.flow_builder.flow import empty_flow, flow_graph_repr, flow_info, flow_to_spec_summary
from flowos_core.graph.flow_builder.layout import layout_flow
from flowos_core.graph.flow_builder.spec import parse_flow_spec

__all__ = [
    "add_component",
    "add_connection",
    "configure_component",
    "empty_flow",
    "flow_graph_repr",
    "flow_info",
    "flow_to_spec_summary",
    "get_component",
    "layout_flow",
    "list_components",
    "list_connections",
    "needs_server_update",
    "parse_flow_spec",
    "remove_component",
    "remove_connection",
]
