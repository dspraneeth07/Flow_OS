"""Entry point for running the FlowOS Agentic MCP server.

This allows running the server with:
    python -m flowos.agentic.mcp
"""

from flowos.agentic.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
