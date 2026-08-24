"""MCP utilities for FlowOS."""

from flowos.api.utils.mcp.config_utils import (
    auto_configure_starter_projects_mcp,
    get_composer_streamable_http_url,
    get_project_sse_url,
    get_project_streamable_http_url,
    get_url_by_os,
)

__all__ = [
    "auto_configure_starter_projects_mcp",
    "get_composer_streamable_http_url",
    "get_project_sse_url",
    "get_project_streamable_http_url",
    "get_url_by_os",
]
