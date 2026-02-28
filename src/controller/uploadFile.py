from fastapi import APIRouter , UploadFile
from fastapi.responses import JSONResponse

from src.service.processFile import chunk_file

router = APIRouter(prefix="/api", tags=["chat"])

@router.post('/upload')
def upload_file(file : UploadFile):
    return  chunk_file(file, 1024)
