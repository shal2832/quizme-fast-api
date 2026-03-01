from fastapi import APIRouter , UploadFile
from fastapi.responses import JSONResponse
from src.models.llama3 import llm_invoke
from src.service.processFile import chunk_file

router = APIRouter(prefix="/api", tags=["chat"])

@router.post('/upload')
def upload_file(file : UploadFile):
    return  chunk_file(file, 1024)

@router.post('/query')
def query_llm(prompt: str):
    res =  llm_invoke(prompt)
    return JSONResponse(content={"message": res}, status_code=200)