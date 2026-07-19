from rag.chunking.legal_chunker import LegalSemanticChunker
from rag.serialization.semantic_serializer import SemanticSerializer


def test_legal_semantic_chunker():
    markdown_content = """# RECOVERY OF POSSESSION OF PREMISES GIVEN ON LEASE ACT, NO. 1 OF 2023
## PARLIAMENT OF SRI LANKA
### SECTION 3: SERVICE OF STATUTORY NOTICE TO QUIT
1. Where a lessee fails to hand over vacant possession, notice shall be served giving 30 days.
"""
    chunker = LegalSemanticChunker()
    chunks = chunker.chunk_markdown(markdown_content, "test_act.md")
    
    assert len(chunks) == 1
    assert chunks[0]["doc_name"] == "test_act.md"
    assert "SECTION 3: SERVICE OF STATUTORY NOTICE TO QUIT" in chunks[0]["section"]


def test_semantic_serializer():
    chunk = {
        "doc_name": "act_no_1_of_2023.md",
        "heading": "SECTION 3",
        "section": "Notice to Quit",
        "text": "Requires 30 days notice to vacate."
    }
    serialized = SemanticSerializer.serialize(chunk)
    assert "Document Source: act_no_1_of_2023.md" in serialized
    assert "Requires 30 days notice to vacate." in serialized
