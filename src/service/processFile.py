import os
import random
from langchain_community.document_loaders import PyMuPDFLoader
from src.service.qdrantApiService import qdrantApiServiceInstance

def chunk_file(content, filename):
    clean_name = os.path.basename(filename)
    temp_file_path = f"/tmp/temp_{random.randint(1, 1000)}_{clean_name}"
    print(f"WRITING TO: {temp_file_path}") 

    with open(temp_file_path, "wb") as f:
        f.write(content)
    print(f"File read successfully")
    qdrantApiServiceInstance.set_file_name(clean_name)
    loader = PyMuPDFLoader(temp_file_path)
    documents = loader.load()
    document_content = []
    for doc in documents:
        doc.metadata["file_id"] = filename
        document_content.append({"page_content": doc.page_content, "metadata": doc.metadata})
    print("Calling split documents API with document content")
    qdrantApiServiceInstance.split_documents_api(document_content)
    print(f"Split documents API response received")
    return temp_file_path