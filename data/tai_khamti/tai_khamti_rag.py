"""
Tai Khamti RAG Service

Responsibilities:
- Keep Tai Khamti retrieval isolated
- Lazy-load the retriever
- Retrieve multiple documents
- Build a clean context for Llama
- Provide source information
"""

from typing import Any, Dict, List, Optional

class TaiKhamtiRAG:
    def __init__(
        self,
        top_k=5
    ):
        self.top_k = top_k
        self.retriever = None
    def load_retriever(self):
        if self.retriever is not None:
            return
        print("=" * 70)
        print("TAI KHAMTI RAG SYSTEM")
        print("=" * 70)
        print(
            "Initializing Tai Khamti Retriever..."
        )

        from data.tai_khamti.tai_khamti_retriever import (
            TaiKhamtiRetriever
        )
        self.retriever = TaiKhamtiRetriever(
            top_k=self.top_k,
            similarity_threshold=0.50
        )
        print(
            "Tai Khamti RAG initialized successfully.")

    def retrieve(
        self,
        question: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve multiple Tai Khamti documents.
        """
        self.load_retriever()

        if top_k is None:
            top_k = self.top_k

        if not question:
            return []

        results = self.retriever.search(
            question=question,
            top_k=top_k
        )

        return results

    # ================================================================
    # BUILD CONTEXT
    # ================================================================

    def build_context(
        self,
        question: str,
        vector_db_path=None,
        language="tai_khamti",
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build multi-document Tai Khamti context.

        vector_db_path and language are retained for compatibility
        with older code.

        This class ALWAYS uses the Tai Khamti knowledge base.
        """

        del vector_db_path
        del language

        results = self.retrieve(
            question=question,
            top_k=top_k
        )
        if not results:
            print(
                "No relevant Tai Khamti documents found."
            )
            return {
                "context": "",
                "sources": [],
                "results": []
            }
        context_parts = []
        sources = []
        for rank, result in enumerate(
            results,
            start=1
        ):
            document_id = result.get(
                "id",
                "Unknown"
            )

            category = result.get(
                "category",
                "Unknown"
            )
            english = result.get(
                "english",
                ""
            ).strip()

            tai_khamti = result.get(
                "tai_khamti",
                ""
            ).strip()

            transliteration = result.get(
                "transliteration",
                ""
            ).strip()
            score = float(
                result.get(
                    "score",
                    0.0
                )
            )
            semantic_score = float(
                result.get(
                    "semantic_score",
                    score
                )
            )
            lexical_score = float(
                result.get(
                    "lexical_score",
                    0.0
                )
            )
            context_parts.append(
                f"""
DOCUMENT {rank}

ID:
{document_id}
CATEGORY:
{category}
ENGLISH:
{english}
TAI KHAMTI:
{tai_khamti}
TRANSLITERATION:
{transliteration}
RELEVANCE SCORE:
{score:.4f}
SEMANTIC SCORE:
{semantic_score:.4f}
LEXICAL SCORE:
{lexical_score:.4f}
""".strip()
            )
            sources.append(
                {
                    "source": "TAI_KHAMTI",
                    "id": document_id,
                    "chunk": document_id,
                    "category": category,
                    "score": score,
                    "similarity": semantic_score,
                    "lexical_score": lexical_score
                }
            )
        context = "\n\n".join(
            context_parts
        )
        print("=" * 70)
        print(
            "TAI KHAMTI RAG CONTEXT CREATED"
        )
        print(
            f"Documents used: {len(results)}"
        )
        print(
            f"Context length: {len(context)}"
        )
        print("=" * 70)
        return {
            "context": context,
            "sources": sources,
            "results": results
        }
    def query(
        self,
        question: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Compatibility method.
        """
        return self.retrieve(
            question=question,
            top_k=top_k
        )
tai_khamti_rag = TaiKhamtiRAG(
    top_k=5
)