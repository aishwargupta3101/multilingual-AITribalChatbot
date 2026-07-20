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
        scores ={}
        for rank,document in enumerate(faiss_documents):
            key =(
                document.page_content,
                document.metadata.get("chunk")
            )
            scores[key] = {
                "document" : document,
                "score":(k-rank)*2
            }
        for rank, document in enumerate(bm25_documents):
            key =(
                document.page_content,
                document.metadata.get("chunk")
            )
            if key in scores :
                scores[key]["score"] += (k-rank)
            else:
                scores[key] ={
                    "document":document,
                    "score":(k-rank)
                }
        ranked =sorted(
            scores.values(),
            key=lambda item: item["score"],
            reverse=True
        )
        return[
            item["document"]
            for item in ranked[:k]
        ]

hybrid_retriever = HybridRetriever()