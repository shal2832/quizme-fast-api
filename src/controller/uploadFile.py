from fastapi import APIRouter , UploadFile
from fastapi.responses import JSONResponse
from src.models.llama3 import llm_invoke
from src.service.processFile import chunk_file
import os
router = APIRouter(prefix="/api", tags=["chat"])

@router.post('/upload')
async def upload_file(file : UploadFile):
    data = await file.read() 
    temp_file_path, serializable_chunks = chunk_file(data, 1024)
    #delete the temp file after processing
    os.remove(temp_file_path)
    return JSONResponse(content={"message": "File processed successfully", "file" : temp_file_path, "chunks": serializable_chunks}, status_code=200)

@router.post('/query')
def query_llm(prompt: str):
    res =  llm_invoke(prompt)
    return JSONResponse(content={"message": res}, status_code=200)