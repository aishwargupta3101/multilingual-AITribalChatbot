from pathlib import Path
from langchain_community.vectorstores import FAISS
from backend.rag.embedding_model import embedding_model

class FAISSManager:
    def create_vector_store(
        self,
        chunks,
        save_path: str
    ):
        vector_store = FAISS.from_texts(
            texts=chunks,
            embedding=embedding_model
        )
        Path(save_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )
        vector_store.save_local(save_path)
        return vector_store
faiss_manager = FAISSManager()
