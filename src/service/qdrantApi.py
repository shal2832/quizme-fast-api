from fastapi import HTTPException
from src.service.rag import Rag
from qdrant_client import models


#To create a collection in qdrant cluster
def create_collection(collection_name):
    try:
        result = Rag().qdrantClient.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        return {"successfully created - ":result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
#delete a collection in qdrant cluster
async def delete_collection(collection_name):
    result = Rag().qdrantClient.delete_collection(collection_name=collection_name)
    return {"Collection {collection_name} successfully deleted. result - :",result}