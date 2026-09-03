from backend.rag.retriever import retriever
from backend.rag.bm25_retriever import bm25_search


class HybridRetriever:
    def retrieve(
        self,
        question: str,
        vector_db_path: str,
        k: int = 4
    ):
        """
        Combine FAISS semantic search and BM25 keyword search
        using Reciprocal Rank-style scoring.
        """
        faiss_documents = retriever.retrieve(
            question=question,
            vector_db_path=vector_db_path,
            k=k
        )
        bm25_documents = bm25_search.retrieve(
            question=question,
            vector_db_path=vector_db_path,
            k=k
        )
        scores = {}
        for rank, document in enumerate(faiss_documents):
            key = (
                document.page_content,
                document.metadata.get("chunk", "")
            )
            scores[key] = {
                "document": document,
                "score": (k - rank) * 2
            }
        for rank, document in enumerate(bm25_documents):
            key = (
                document.page_content,
                document.metadata.get("chunk", "")
            )
            if key in scores:
                scores[key]["score"] += (k - rank)
            else:
                scores[key] = {
                    "document": document,
                    "score": k - rank
                }
        ranked = sorted(
            scores.values(),
            key=lambda item: item["score"],
            reverse=True
        )
        results = []

        for item in ranked[:k]:
            document = item["document"]
            print("=" * 60)
            print("HYBRID RETRIEVER DOCUMENT")
            print("Metadata:", document.metadata)
            print("Content:", document.page_content[:200])
            print("=" * 60)
            document.metadata.setdefault(
                "source",
                "TAI_KHAMTI"
            )
            document.metadata.setdefault(
                "chunk",
                "Unknown"
            )
            document.metadata.setdefault(
                "category",
                "Unknown"
            )
            results.append(document)
        return results
hybrid_retriever = HybridRetriever()