from langchain_community.document_loaders import PyMuPDFLoader
from src.service.rag import Rag

def chunk_file(content, chunk_size):
    """
    Process a PDF file and add its chunks to the Qdrant collection.
    Automatically creates the collection if it doesn't exist.
    
    Args:
        content: File content (bytes)
        chunk_size: Size of chunks for splitting
        
    Returns:
        Tuple of (temp_file_path, serializable_chunks)
    """
    temp_file_path = "temp_file.pdf"
    
    # Initialize RAG instance - this will ensure collection exists
    rag = Rag()
    
    # Write file to disk
    with open(temp_file_path, "wb") as f:
        f.write(content)
    print(f"File read successfully")
    
    # Load and process documents
    loader = PyMuPDFLoader(temp_file_path)
    documents = loader.load()
    
    # Split documents into chunks
    docs = rag.textSplitter.create_documents([doc.page_content for doc in documents])
    
    # Create serializable chunks for API response
    serializable_chunks = [
        {"page_content": doc.page_content, "metadata": doc.metadata} 
        for doc in docs
    ]
    
    # Add documents to vector store
    print(f"Adding {len(docs)} chunks to collection '{rag.collectionName}'...")
    rag.vector_store.add_documents(docs)
    
    print(f"Successfully added {len(docs)} chunks to Qdrant collection")
    
    return temp_file_path, serializable_chunks

