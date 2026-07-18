from langchain_community.retrievers import BM25Retriever
from backend.rag.faiss_manager import faiss_manager

class BM25Search:
    def retrieve(
        self,
        question:str,
        vector_db_path: str,
        k:int =4
    ):
        vector_store = faiss_manager.load_vector_store(
            vector_db_path
        )
        documents = vector_store.similarity_search(
            "",
            k=1000
        )
        bm25 = BM25Retriever.from_documents(
            documents
        )
        bm25.k = k
        return bm25.invoke(question)
bm25_search = BM25Search()