import os
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi import HTTPException


class qdrantService:

    collectionName = 'pdf_chunks'
    
    def __init__(self):
        self.file_name = None
        self.qdrantClient = QdrantClient(
            url= os.getenv("QDRANT_CLUSTER_URL"),
            api_key= os.getenv("QDRANT_API_KEY")
        )
        self.textSplitter = RecursiveCharacterTextSplitter(
            chunk_size= 1000,
            chunk_overlap=100
        )
        self.hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.check_collection_exists()
        self.vector_store = QdrantVectorStore(
            client=self.qdrantClient,
            collection_name=self.collectionName,
            embedding=self.hf_embeddings
        )
        # This tells Qdrant to build a "Keyword" index for your file_id field
        try:
            self.qdrantClient.create_payload_index(
                collection_name=self.collectionName,
                field_name="metadata.file_id",
                field_schema=rest.PayloadSchemaType.KEYWORD,
            )
            print(f"Payload index created for metadata.file_id")
        except Exception as e:
            print(f"Note: Payload index creation skipped or failed (may already exist): {e}")
        

    def set_file_name(self, file_name):
        """
        Get the file name from user input and set it to class variable file_name for all context retreival"

        Args:
            file_name: name of the file uploaded by the user
        """
        self.file_name = file_name
        print(f"File name set to: {self.file_name} for context retrieval.")

    def check_collection_exists(self):
        """
        Check if the collection exists in Qdrant, if not create it.
        
        """
        existing_collection_names = self.get_collections()
        print(f"Existing collections in Qdrant: {existing_collection_names}")

        if self.collectionName not in existing_collection_names:
            self.create_collection(self.collectionName)
            print(f"Collection {self.collectionName} created successfully:")
    
    def create_collection(self,collection_name):
        """
        Create a collection in Qdrant with the specified name.

        """
        try:
            result = self.qdrantClient.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
            return {"successfully created - ":result}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def delete_collection(self, collection_name):
        """
        Delete a collection in Qdrant with the specified name.
        
        Args:
            collection_name (str): The name of the collection to delete.
        """

        result = self.qdrantClient.delete_collection(collection_name=collection_name)
        return {"Collection {collection_name} successfully deleted. result - ":result}
    
    def get_collections(self):
        """
        Retrieve the list of existing collections in Qdrant.
        
        Returns:
            list: A list of collection names.
        """
        collections = self.qdrantClient.get_collections().collections
        return [c.name for c in collections]
    
    def query_context_retrieval(self, query : str):
        """
        Retrieve relevant context from Qdrant based on the input query.

        Args:
            query (str): The input query for which to retrieve context.

        Returns:
            str: The concatenated context retrieved from the Qdrant collection.
        """
        try:
            self.vector_store.from_existing_collection(
                embedding=self.hf_embeddings,
                collection_name=self.collectionName,
                url=os.getenv("QDRANT_CLUSTER_URL"),
                api_key= os.getenv("QDRANT_API_KEY")
            )
            print(f"Vector store initialized with collection '{self.collectionName}' for context retrieval.")
            relevant_chunks = self.vector_store.similarity_search(query, k=5)
            return ".\n".join([chunk.page_content for chunk in relevant_chunks])
        except Exception as e:
            print(f"Error: {e}, Provided collection not present to fetch the context for the query.")
            return ""
    
    def entire_context_retrieval(self):
        """
        Retrieve the entire context from Qdrant collection.

        Returns:
            str: The concatenated context retrieved from the Qdrant collection.
        """
        try:
            print(f"Retrieving all documents from collection '{self.collectionName}'.")
            # Use scroll to retrieve all documents from the collection
            all_points, _ = self.qdrantClient.scroll(
                collection_name=self.collectionName,
                limit=1000  # Adjust limit if you have more documents
            )
            
            # Extract page content from all points
            all_content = []
            for point in all_points:
                if point.payload and 'page_content' in point.payload:
                    all_content.append(point.payload['page_content'])
            
            context = ".\n".join(all_content)
            print(f"Retrieved {len(all_content)} documents from collection.")
            return context
        except Exception as e:
            print(f"Error: {e}, Failed to fetch entire context.")
            return ""

# Create the instance here
qdrant_service_instance = qdrantService()