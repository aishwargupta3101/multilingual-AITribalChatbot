"""
Tai Khamti RAG Compatibility Wrapper
-------------------------------------

The actual Tai Khamti RAG implementation lives in:

    data/tai_khamti/tai_khamti_rag.py

This file exists only for compatibility with older imports such as:

    from backend.rag.tai_khamti_rag import tai_khamti_rag

IMPORTANT:
- Tai Khamti uses ONLY the Tai Khamti knowledge base.
- No normal vector database is used here.
- No fallback to the normal RAG system is performed.
- The Tai Khamti retriever is loaded lazily.
"""

from data.tai_khamti.tai_khamti_rag import (
    TaiKhamtiRAG,
    tai_khamti_rag,
)
__all__ = [
    "TaiKhamtiRAG",
    "tai_khamti_rag",
]