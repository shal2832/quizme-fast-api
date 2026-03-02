import os
from typing import List, Optional
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models
from langchain_huggingface import HuggingFaceEmbeddings


class Rag:
    def __init__(self, collection_name: str = 'pdf_chunks'):
        """Initialize RAG pipeline with Qdrant vector store"""
        self.collectionName = collection_name
        self.qdrantClient = QdrantClient(
            url=os.getenv("QDRANT_CLUSTER_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.textSplitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        self.hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Check if collection exists and create if needed BEFORE creating vector store
        self._ensure_collection_exists()
        
        # Now create the vector store with the verified collection
        self.vector_store = QdrantVectorStore(
            client=self.qdrantClient,
            collection_name=self.collectionName,
            embedding=self.hf_embeddings
        )
        
        print(f"Collection '{self.collectionName}' is ready")

    def _ensure_collection_exists(self) -> None:
        """
        Ensure the collection exists in Qdrant.
        Creates it if it doesn't exist.
        """
        try:
            collections = self.qdrantClient.get_collections().collections
            existing_names = [c.name for c in collections]
            print(f"Existing collections: {existing_names}")
            
            if self.collectionName not in existing_names:
                print(f"Collection '{self.collectionName}' not found. Creating...")
                self.qdrantClient.create_collection(
                    collection_name=self.collectionName,
                    vectors_config=models.VectorParams(
                        size=384,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"Collection '{self.collectionName}' created successfully")
            else:
                print(f"Collection '{self.collectionName}' already exists")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
            raise

    def retrieve_documents(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve documents from Qdrant collection based on similarity search
        
        Args:
            query: The search query
            top_k: Number of top documents to retrieve (default: 5)
            
        Returns:
            List of Document objects from the vector store
        """
        try:
            results = self.vector_store.similarity_search(query, k=top_k)
            return results
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def retrieve_all_documents(self) -> List[Document]:
        """
        Retrieve all documents from the Qdrant collection
        
        Returns:
            List of all Document objects in the collection
        """
        try:
            # Scroll through the collection to get all points
            scroll_filter = None
            all_documents = []
            limit = 100
            offset = 0
            
            while True:
                points, next_offset = self.qdrantClient.scroll(
                    collection_name=self.collectionName,
                    limit=limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                if not points:
                    break
                
                for point in points:
                    doc = Document(
                        page_content=point.payload.get('page_content', ''),
                        metadata=point.payload.get('metadata', {})
                    )
                    all_documents.append(doc)
                
                if not next_offset:
                    break
                offset = next_offset
            
            print(f"Retrieved {len(all_documents)} documents from {self.collectionName}")
            return all_documents
            
        except Exception as e:
            print(f"Error retrieving all documents: {e}")
            return []

    def get_retriever(self, top_k: int = 5):
        """
        Get a retriever object for use in RAG chains
        
        Args:
            top_k: Number of documents to retrieve per query
            
        Returns:
            Retriever object from the vector store
        """
        return self.vector_store.as_retriever(search_kwargs={"k": top_k})

    def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Delete a collection from Qdrant
        
        Args:
            collection_name: Name of the collection to delete. If None, deletes the default collection.
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            col_name = collection_name or self.collectionName
            self.qdrantClient.delete_collection(collection_name=col_name)
            print(f"Collection '{col_name}' deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False

    def recreate_collection(self) -> bool:
        """
        Recreate the collection after deletion.
        Uses _ensure_collection_exists to safely recreate.
        
        Returns:
            True if recreation was successful, False otherwise
        """
        try:
            self._ensure_collection_exists()
            return True
        except Exception as e:
            print(f"Error recreating collection: {e}")
            return False

    

    