from langchain_community.document_loaders import PyMuPDFLoader
from src.service.rag import Rag

def chunk_file(content, chunk_size):
    temp_file_path = "temp_file.pdf"
    with open(temp_file_path, "wb") as f:
        f.write(content)
    print(f"File read successfully")

    loader = PyMuPDFLoader(temp_file_path)
    documents = loader.load()
    docs = Rag().textSplitter.create_documents([doc.page_content for doc in documents])
    # for passing in api response only
    serializable_chunks = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]

    Rag().vector_store.add_documents(docs)
    return temp_file_path, serializable_chunks