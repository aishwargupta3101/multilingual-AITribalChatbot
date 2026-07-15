from backend.database.collections import collections
from datetime import datetime
class DocumentRepository:
    async   def save_document(
        self,
        session_id:str,
        original_filename:str,
        filename:str,
        file_size:int,
        file_type:str,
    ):
        document ={
            "session_id":session_id,
            "filename": filename,
            "original_filename":original_filename,
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