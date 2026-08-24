MAX_MCP_SERVER_NAME_LENGTH = 30
MAX_MCP_TOOL_NAME_LENGTH = 30

# Prefix for auto-generated MCP server names (what a user sees in their agent's
# config, e.g. "flowos-starter_project").
MCP_SERVER_NAME_PREFIX = "flowos-"

# Chars left for the project name once the prefix is applied. Derived rather than
# hardcoded so a longer prefix can't silently overflow MAX_MCP_SERVER_NAME_LENGTH.
MAX_MCP_SERVER_NAME_BODY_LENGTH = MAX_MCP_SERVER_NAME_LENGTH - len(MCP_SERVER_NAME_PREFIX) - 1
