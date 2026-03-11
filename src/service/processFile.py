from langchain_community.document_loaders import PyMuPDFLoader
from src.service.qdrantApiService import qdrantApiServiceInstance
import random
def chunk_file(content, filename):
    temp_file_path = f"/tmp/temp_{random.randint(1, 1000)}_{filename}"
    with open(temp_file_path, "wb") as f:
        f.write(content)
    print(f"File read successfully")

    loader = PyMuPDFLoader(temp_file_path)
    documents = loader.load()
    document_content = []
    for doc in documents:
        doc.metadata["file_id"] = filename
        document_content.append({"page_content": doc.page_content, "metadata": doc.metadata})
    docs = qdrantApiServiceInstance.split_documents_api(document_content)
    # for passing in api response only
    serializable_chunks = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs.json().get("documents", [])
    ]

    #pass the file name inside qdrant service, so that it can be used when retrieving context
    ### qdrant_service_instance.set_file_name(filename)
    qdrantApiServiceInstance.add_documents_api(docs)
    return temp_file_path, serializable_chunks