from backend.rag.hybrid_retriever import hybrid_retriever
class RAGService:
    def build_context(
        self,
        question: str,
        vector_db_path: str
    ):
        documents = hybrid_retriever.retrieve(
            question=question,
            vector_db_path=vector_db_path,
            k=4
        )
        if not documents:
            return {
                "context": "",
                "sources": []
            }
        context = "\n\n".join(
            document.page_content
            for document in documents
        )
        sources = []
        for document in documents:
            sources.append(
                {
                    "source": document.metadata.get(
                        "source",
                        "Unknown"
                    ),
                    "chunk": document.metadata.get(
                        "chunk",
                        "Unknown"
                    )
                }
            )
        return {
            "context": context,
            "sources": sources
        }
rag_service = RAGService()