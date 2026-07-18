from backend.database.collections import collections
from datetime import datetime
class DocumentRepository:
    async   def save_document(
        self,
        session_id:str,
        document_id:str,
        original_filename:str,
        filename:str,
        file_path:str,
        vector_db_path:str,
        file_size: int,
        file_type:str,
    ):
        document ={
            "document_id":document_id,
            "session_id":session_id,
            "filename": filename,
            "original_filename":original_filename,
            "file_path":file_path,
            "vector_db_path": vector_db_path,
            "file_size":file_size,
            "file_type":file_type,
            "status":"uploaded",
            "uploaded_at":datetime.utcnow(),
        }
        result = await collections.documents.insert_one(document)
        return str(result.inserted_id)
    async  def get_documents(
            self,
            session_id :str,
    ):
        cursor = collections.documents.find(
            {
                "session_id": session_id
            }
        )
        documents= await cursor.to_list(length=100)
        for document in documents:
            document["_id"] = str(document["_id"])
        return documents
    async def get_document_by_id(
        self,
        document_id:str,
    ):
        document = await collections.documents.find_one(
            {
                "document_id": document_id
            }
        )
        if document:
            document["_id"] = str(document["_id"])
        return document
    async def get_latest_document(
        self,
        session_id:str
    ):
        document =await collections.documents.find_one(
            {
                "session_id":session_id
            },
            sort=[("uploaded_at",-1)]
        )
        if document:
            document["_id"] = str(document["_id"])
        return document

    async def delete_document(
        self,
        filename:str
    ):
        await collections.documents.delete_one(
            {
                "filename":filename
            }
        )

document_repository =DocumentRepository()