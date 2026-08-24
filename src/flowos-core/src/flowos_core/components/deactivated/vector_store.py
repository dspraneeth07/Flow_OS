from langchain_core.vectorstores import VectorStoreRetriever

from flowos_core.custom.custom_component.custom_component import CustomComponent
from flowos_core.field_typing import VectorStore
from flowos_core.inputs.inputs import HandleInput


class VectorStoreRetrieverComponent(CustomComponent):
    display_name = "VectorStore Retriever"
    description = "A vector store retriever"
    name = "VectorStoreRetriever"
    icon = "LangChain"

    inputs = [
        HandleInput(
            name="vectorstore",
            display_name="Vector Store",
            input_types=["VectorStore"],
            required=True,
        ),
    ]

    def build(self, vectorstore: VectorStore) -> VectorStoreRetriever:
        return vectorstore.as_retriever()
