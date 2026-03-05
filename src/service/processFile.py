from langchain_community.document_loaders import PyMuPDFLoader
from src.service.qdrantService import qdrant_service_instance

def chunk_file(content, filename):
    temp_file_path = f"temp_{filename}"
    with open(temp_file_path, "wb") as f:
        f.write(content)
    print(f"File read successfully")

    loader = PyMuPDFLoader(temp_file_path)
    documents = loader.load()
    qdrant_service_instance.check_collection_exists()
    docs = qdrant_service_instance.textSplitter.create_documents([doc.page_content for doc in documents])
    for doc in docs:
        doc.metadata["file_id"] = filename
    # for passing in api response only
    serializable_chunks = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]

    #pass the file name inside qdrant service, so that it can be used when retrieving context
    qdrant_service_instance.set_file_name(filename)
    qdrant_service_instance.vector_store.add_documents(docs)
    return temp_file_path, serializable_chunks