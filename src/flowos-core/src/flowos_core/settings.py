"""Settings constants for flowos_core package."""

import os

# Development mode flag - can be overridden by environment variable
DEV = os.getenv("FLOWOS_DEV", "false").lower() == "true"
