"""Logging module for flowos_core package."""

from flowos_core.log._streams import make_streams_resilient
from flowos_core.log.logger import configure, logger

make_streams_resilient()

__all__ = ["configure", "logger"]
