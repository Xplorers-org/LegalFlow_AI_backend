import re
from typing import List, Dict, Any


class LegalSemanticChunker:
    """Intelligent semantic chunker for legal statutes and contracts.
    
    Breaks text down by Document Title, Section Headings, and Clause numbers
    rather than arbitrary token counts, maintaining structural parent-child links.
    """

    def __init__(self):
        # Regex patterns for Sri Lankan Act sections, headings, and clause identifiers
        self.section_pattern = re.compile(r'^(###?\s+SECTION\s+\d+:?.*|^###?\s+[A-Z0-9\s,–\-]+)', re.MULTILINE)
        self.clause_pattern = re.compile(r'^(\d+\.\s+|[a-z]\)\s+|SECTION\s+\d+)', re.MULTILINE)

    def chunk_markdown(self, markdown_text: str, doc_name: str) -> List[Dict[str, Any]]:
        """Splits legal markdown documents into structural chunks with heading metadata."""
        lines = markdown_text.split('\n')
        chunks = []

        current_heading = "Preamble"
        current_section = "General"
        current_lines = []

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("# "):
                doc_title = line_str.replace("# ", "").strip()
                continue
            elif line_str.startswith("## "):
                current_heading = line_str.replace("## ", "").strip()
                continue
            elif line_str.startswith("### "):
                if current_lines:
                    text_content = "\n".join(current_lines).strip()
                    if text_content:
                        chunks.append({
                            "text": text_content,
                            "doc_name": doc_name,
                            "heading": current_heading,
                            "section": current_section,
                        })
                    current_lines = []
                current_section = line_str.replace("### ", "").strip()
                continue

            if line_str:
                current_lines.append(line_str)

        if current_lines:
            text_content = "\n".join(current_lines).strip()
            if text_content:
                chunks.append({
                    "text": text_content,
                    "doc_name": doc_name,
                    "heading": current_heading,
                    "section": current_section,
                })

        return chunks
