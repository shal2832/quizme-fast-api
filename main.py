from fastapi import FastAPI
from src.controller.uploadFile import router as chat_router

app = FastAPI()

# Include routers from different service modules
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
