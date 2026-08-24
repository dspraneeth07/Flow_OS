"""flowos-arxiv: arXiv Search bundle.

This package is the distribution unit ``flowos-arxiv``.  At runtime
FlowOS's loader discovers ``extension.json`` shipped alongside this
``__init__.py`` and registers ``ArXivComponent`` under the namespaced
ID ``ext:arxiv:ArXivComponent@official``.

Second pilot port (after flowos-duckduckgo) -- exercises the same
extraction recipe documented in ``src/bundles/PORTING.md`` against a
component with no third-party runtime deps.
"""

from flowos_arxiv.components.arxiv.arxiv import ArXivComponent

__all__ = ["ArXivComponent"]
