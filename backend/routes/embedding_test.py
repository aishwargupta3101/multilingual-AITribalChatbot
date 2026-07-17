from fastapi import APIRouter
from backend.rag.embedding_model import embedding_model

router = APIRouter()
@router.get("/embedding-test")
async def embedding_test():
    vector = embedding_model.embed_query(
        "Artificial Intelligence"
    )
    return{
        "dimension":len(vector),
        "first_10_values": vector[:10]
    }