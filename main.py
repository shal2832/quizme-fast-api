import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
## for deployment
# Load environment variables from .env file
load_dotenv()


from fastapi import FastAPI
from src.controller.uploadFile import router as chat_router


app = FastAPI()
# Read the allowed frontend origins from the environment configuration
raw_origins = os.getenv("ALLOWED_ORIGINS", "")

if raw_origins:
    origins = [origin.strip() for origin in raw_origins.split(",")]
else:
    # Safe default fallback for local web development tools
    origins = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers from different service modules
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
