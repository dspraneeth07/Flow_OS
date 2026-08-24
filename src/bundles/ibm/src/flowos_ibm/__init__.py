"""flowos-ibm: IBM bundle (Db2 Vector Store + watsonx.ai LLM and embeddings).

This package is the distribution unit ``flowos-ibm``.  At runtime
FlowOS's loader discovers ``extension.json`` shipped alongside this
``__init__.py`` and registers the three IBM components under the
namespaced IDs:

* ``ext:ibm:DB2VectorStoreComponent@official``
* ``ext:ibm:WatsonxAIComponent@official``
* ``ext:ibm:WatsonxEmbeddingsComponent@official``

Third pilot port (after flowos-duckduckgo and flowos-arxiv) -- exercises the
same extraction recipe documented in ``src/bundles/PORTING.md`` against
a multi-component bundle that ships a langchain-community-backed vector
store, the IBM Db2 vendor SDK, and the langchain-ibm watsonx.ai client.
"""

from flowos_ibm.components.ibm.db2_vector import DB2VectorStoreComponent
from flowos_ibm.components.ibm.watsonx import WatsonxAIComponent
from flowos_ibm.components.ibm.watsonx_embeddings import WatsonxEmbeddingsComponent

__all__ = [
    "DB2VectorStoreComponent",
    "WatsonxAIComponent",
    "WatsonxEmbeddingsComponent",
]
