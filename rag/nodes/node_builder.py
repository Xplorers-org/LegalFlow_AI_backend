from typing import List, Dict, Any
from llama_index.core.schema import TextNode


class NodeBuilder:
    """Converts serialized legal chunks into LlamaIndex TextNode objects populated with rich metadata."""

    @staticmethod
    def build_nodes(chunks: List[Dict[str, Any]]) -> List[TextNode]:
        """Maps serialized chunks to LlamaIndex TextNodes."""
        nodes = []
        for idx, chunk in enumerate(chunks):
            node = TextNode(
                text=chunk["serialized_text"],
                id_=f"{chunk['doc_name']}_{idx}",
                metadata={
                    "doc_name": chunk["doc_name"],
                    "heading": chunk["heading"],
                    "section": chunk["section"],
                    "chunk_index": idx,
                    "raw_text": chunk["text"],
                }
            )
            nodes.append(node)
        return nodes
