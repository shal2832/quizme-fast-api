import httpx
import os

class qdrantApiService:

    def set_file_name(self, file_name : str):
        with httpx.Client() as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/set-file",
                json={"file_name": file_name}
            )
            print(f"Set file name API response: {response.json()}")
            return response
    
    def list_collections_api(self):
        with httpx.Client() as client:
            response = client.get(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/collections"
            )
            return response
        
    def split_documents_api(self, documents: list):
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/split-documents",
                json={"documents": documents}
            )
            return response.json().get("documents")
    
    def add_documents_api(self, documents: list):
        with httpx.Client() as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/store-documents",
                json={"documents": documents}
            )
            return response
        
    def query_api(self, query: str):
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{os.getenv('QDRANT_SERVICE_URL')}/qdrant/query",
                json={"query": query}
            )
            return response
        
    def entire_context_api(self):
        with httpx.Client(timeout=120.0) as client:
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