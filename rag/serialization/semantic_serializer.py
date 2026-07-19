from typing import Dict, Any


class SemanticSerializer:
    """Converts structured legal text chunks into enriched, context-aware serialized text strings
    ideal for vector embedding representation.
    """

    @staticmethod
    def serialize(chunk: Dict[str, Any]) -> str:
        """Enriches raw chunk text with document title, section heading, and structural hierarchy context."""
        serialized_text = (
            f"Document Source: {chunk['doc_name']}\n"
            f"Category / Heading: {chunk['heading']}\n"
            f"Section / Provision: {chunk['section']}\n"
            f"Content Excerpt:\n{chunk['text']}"
        )
        return serialized_text
