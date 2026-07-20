from langchain_core.documents import Document

from backend.rag.faiss_manager import faiss_manager

class Retriever:
    def retrieve(
        self,
        question: str,
        vector_db_path: str,
        k: int = 4
    ) -> list[Document]:
        """
        Retrieve the most relevant documents from the FAISS vector store.
        """
        vector_store = faiss_manager.load_vector_store(
            vector_db_path
        )
        if vector_store is None:
            return []
        documents = vector_store.similarity_search(
            query=question,
            k=k
        )
        return documents
retriever = Retriever()