from fastapi import APIRouter , UploadFile
from fastapi.responses import JSONResponse
from src.models.llama3 import llm_invoke
from src.service.processFile import chunk_file
import os
router = APIRouter(prefix="/api", tags=["chat"])

@router.post('/upload')
async def upload_file(file : UploadFile):
    """
    Endpoint to handle file uploads. It reads the uploaded file, processes it, and returns a response indicating success.
    
    Args:
        file (UploadFile): The file uploaded by the user.

    Returns:
        JSONResponse: A response containing a success message, the file name, and the number of chunks created from the file.
    """
    data = await file.read() 
    temp_file_path, serializable_chunks = chunk_file(data)
    #delete the temp file after processing
    os.remove(temp_file_path)
    return JSONResponse(content={"message": "File processed successfully", "file" : temp_file_path, "number of chunks": len(serializable_chunks)}, status_code=200)

@router.post('/query')
def query_llm(prompt: str):
    """
    Endpoint to handle queries to the LLM. It takes a prompt as input, retrieves relevant context, and returns the LLM's response.
    
    Args:
        prompt (str): The query or prompt to be sent to the LLM.

    Returns:
        JSONResponse: A response containing the LLM's answer to the query.
    """
    res =  llm_invoke(prompt)
    return JSONResponse(content={"message": res}, status_code=200)

