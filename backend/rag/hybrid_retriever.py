from backend.rag.retriever import retriever
from backend.rag.bm25_retriever import bm25_search

class HybridRetriever:
    def retrieve(
        self,
        question:str,
        vector_db_path:str,
        k:int =4
    ):
        """
        Combine FAISS semantic search and BM25 keyword search.
        """
        faiss_documents= retriever.retrieve(
            question=question,
            vector_db_path=vector_db_path,
            k=k
        )
        bm25_documents= bm25_search.retrieve(
            question=question,
            vector_db_path=vector_db_path,
            k=k
        )
        merged_documents = []

        seen = set()
        for document in faiss_documents+ bm25_documents:
            key=(
                document.page_content,
                document.metadata.get("chunk")
            )
            if key not in seen:
                seen.add(key)
                merged_documents.append(document)
        return merged_documents
hybrid_retriever = HybridRetriever()