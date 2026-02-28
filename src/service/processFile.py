from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="", tags=["chat"])

@router.post('/chat')
def chat(message: str):
    return JSONResponse(content={"Your message": message}, status_code=200)
