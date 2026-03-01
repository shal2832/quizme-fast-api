import os
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
from langchain_huggingface import HuggingFaceEmbeddings


class Rag:
    def __init__(self):
        self.collectionName = 'pdf_chunks'
        self.qdrantClient = QdrantClient(
            url=os.getenv("qdrant_cluster_url"),
            api_key=os.getenv("qdrant_api_key")
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
        
        collections = self.qdrantClient.get_collections().collections
        print(f"Existing collections: {[c.name for c in collections]}")
        existing_names = [c.name for c in collections]

        if self.collectionName not in existing_names:
            self.qdrantClient.create_collection(
                collection_name=self.collectionName,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
        print(f"Collection {self.collectionName} created successfully:")


    

    