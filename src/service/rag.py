import os
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
from langchain_huggingface import HuggingFaceEmbeddings


class Rag:
    def __init__(self):
        from src.service.qdrantApi import create_collection
        
        self.collectionName = 'pdf_chunks'
        self.qdrantClient = QdrantClient(
            url= os.getenv("qdrant_cluster_url"),
            api_key= os.getenv("qdrant_api_key")
        )
        self.textSplitter = RecursiveCharacterTextSplitter(
            chunk_size= 1000,
            chunk_overlap=100
        )
        self.hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = QdrantVectorStore(
            client=self.qdrantClient,
            collection_name=self.collectionName,
            embedding=self.hf_embeddings
        )
        existing_collection_names = self.get_collections()
        print(f"Existing collections in Qdrant: {existing_collection_names}")
        if self.collectionName not in existing_collection_names:
            create_collection(self.collectionName)
        print(f"Collection {self.collectionName} created successfully:")

    def get_collections(self):
        collections = self.qdrantClient.get_collections().collections
        print(f"Existing collections: {[c.name for c in collections]}")
        return [c.name for c in collections]
    
    def context_retrieval(self, query : str):
        try:
            self.vector_store.from_existing_collection(
                embedding=self.hf_embeddings,
                collection_name=self.collectionName,
                url=os.getenv("qdrant_cluster_url"),
                api_key= os.getenv("qdrant_api_key")
            )
            print(f"Vector store initialized with collection '{self.collectionName}' for context retrieval.")
            relevant_chunks = self.vector_store.similarity_search(query, k=5)
            print(f"Relevant chunks retrieved for query '{query}': {[chunk.page_content for chunk in relevant_chunks]}")
            return ".\n".join([chunk.page_content for chunk in relevant_chunks])
        except Exception as e:
            print(f"Error: {e}, Provided collection not present to fetch the context for the query.")





    

    