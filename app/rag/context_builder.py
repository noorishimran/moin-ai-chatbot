"""
3.7 Context assembly.
"""

from app.rag.retriever import RetrievedChunk


def build_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return ""

    sections = []
    for chunk in chunks:
        category_label = f" ({chunk.category})" if chunk.category else ""
        sections.append(f"### {chunk.title}{category_label}\n{chunk.content}")

    return "\n\n".join(sections)