"""Entry point for the FlowOS MCP server.

Usage:
    python -m flowos_core.mcp
    # or via console script:
    flowos-mcp

Environment variables:
    FLOWOS_SERVER_URL: FlowOS server URL (default: http://localhost:7860)
    FLOWOS_API_KEY: API key for authentication (skips login)
"""

from flowos_core.mcp.server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
