from backend.rag.embedding_model import embedding_model
class RAGService:
    def create_embeddings(
        self,
        chunks
    ):
        embeddings = embedding_model.embed_documents(
            chunks
        )
        return embeddings

rag_service = RAGService()