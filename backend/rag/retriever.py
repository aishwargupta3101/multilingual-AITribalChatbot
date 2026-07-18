
from backend.rag.faiss_manager import faiss_manager
class Retriever:
    def retrieve(
        self,
        question:str,
        vector_db_path:str,
        k:int =4
    ):
        """
        Retrieve the most relevant document chunks.
        """
        vector_store = faiss_manager.load_vector_store(
            vector_db_path
        )
        documents= vector_store.similarity_search(
            query=question,
            k=k
        )
        return documents

retriever = Retriever()