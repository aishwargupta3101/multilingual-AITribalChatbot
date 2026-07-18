from pathlib import Path
from langchain_community.vectorstores import FAISS
from backend.rag.embedding_model import embedding_model

class FAISSManager:
    """
    Handles creation,saving,loading and deletion
    of FAISS vector databases.
    """
    def create_vector_store(
        self,
        documents
    ):
        """
        Create a FAISS vector store from document chunks.
        """
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_model
        )
        return vector_store
    def save_vector_store(self,vector_store,save_path:str):
        """
        Save FAISS vector store locally.
        """
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True,exist_ok=True)
        vector_store.save_local(str(save_dir))
    def load_vector_store(self,save_path:str):
        """
        Load an existing FAISS vector store.
        """
        save_dir =Path(save_path)
        if not save_dir.exists():
            raise FileNotFoundError(
                f"Vector database not found :{save_dir}"
            )
        return FAISS.load_local(
            folder_path=str(save_dir),
            embeddings=embedding_model,
            allow_dangerous_deserialization=True
        )
    def create_and_save(self,documents,save_path:str):
        """
        Convenience method:
        Create vector store and save it.
        """
        vector_store = self.create_vector_store(documents)
        self.save_vector_store(
            vector_store,
            save_path
        )
        return vector_store

faiss_manager = FAISSManager()
