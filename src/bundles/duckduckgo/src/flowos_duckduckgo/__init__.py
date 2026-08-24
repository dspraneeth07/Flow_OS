"""flowos-duckduckgo: DuckDuckGo Search bundle.

This package is the distribution unit ``flowos-duckduckgo``.  At runtime
FlowOS's loader discovers ``extension.json`` shipped alongside this
``__init__.py`` and registers ``DuckDuckGoSearchComponent`` under the
namespaced ID ``ext:duckduckgo:DuckDuckGoSearchComponent@official``.

The first provider extracted from ``flowos_core.components.<provider>`` into
a standalone Bundle.
"""

from flowos_duckduckgo.components.duckduckgo.duck_duck_go_search_run import (
    DuckDuckGoSearchComponent,
)

__all__ = ["DuckDuckGoSearchComponent"]
