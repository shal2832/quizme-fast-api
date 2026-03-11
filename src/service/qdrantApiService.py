import httpx
import os

class qdrantApiService:

    def list_collections_api(self):
        with httpx.Client() as client:
            response = client.get(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/collections"
            )
            return response
        
    def split_documents_api(self, documents: list):
        with httpx.Client() as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/split-documents",
                json={"documents": documents}
            )
            return response
    
    def add_documents_api(self, documents: list):
        with httpx.Client() as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/store-documents",
                json={"documents": documents}
            )
            return response
        
    def query_api(self, query: str):
        with httpx.Client() as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/query",
                json={"query": query}
            )
            return response
        
    def entire_context_api(self):
        with httpx.Client() as client:
            response = client.get(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/entire-context"
            )
            return response
        
    def delete_api(self, collection_name):
        with httpx.Client() as client:
            response = client.delete(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/collection/{collection_name}"
            )
            return response
qdrantApiServiceInstance = qdrantApiService()