from fastapi import APIRouter, UploadFile, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.models.llama3 import llm_invoke
from src.service.processFile import chunk_file
from src.service.prepareMCQ import MCQGenerator
import os

router = APIRouter(prefix="/api", tags=["chat"])


class MCQRequest(BaseModel):
    """Request model for MCQ generation"""
    query: str
    num_questions: int = 5
    top_k: int = 5


class MCQAllRequest(BaseModel):
    """Request model for MCQ generation from all documents"""
    num_questions: int = 10
    batch_size: int = 5


@router.post('/upload')
async def upload_file(file: UploadFile):
    """Upload and process a file, storing chunks in Qdrant"""
    data = await file.read() 
    temp_file_path, serializable_chunks = chunk_file(data, 1024)
    # delete the temp file after processing
    os.remove(temp_file_path)
    return JSONResponse(
        content={
            "message": "File processed successfully", 
            "file": temp_file_path, 
            "chunks": serializable_chunks
        }, 
        status_code=200
    )


@router.post('/query')
def query_llm(prompt: str):
    """Query the LLM directly"""
    res = llm_invoke(prompt)
    return JSONResponse(content={"message": res}, status_code=200)


@router.post("/questions/query")
async def generate_questions_from_query(request: MCQRequest):
    """
    Generate MCQs based on a specific query.
    Retrieves relevant documents from Qdrant and generates MCQs.
    """
    try:
        generator = MCQGenerator()
        result = generator.generate_mcq_from_query(
            query=request.query,
            num_questions=request.num_questions,
            top_k=request.top_k
        )
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "message": "Failed to generate questions"},
            status_code=500
        )


@router.post("/questions/all")
async def generate_questions_from_all(request: MCQAllRequest):
    """
    Generate MCQs from all documents in the Qdrant collection.
    Processes all documents in batches and generates a comprehensive set of MCQs.
    """
    try:
        generator = MCQGenerator()
        questions = generator.generate_mcq_from_all_content(
            num_questions=request.num_questions,
            batch_size=request.batch_size
        )
        return JSONResponse(
            content={
                "message": "MCQs generated successfully from all documents",
                "total_questions": len(questions),
                "questions": questions,
                "status": "success"
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "message": "Failed to generate questions from all documents"},
            status_code=500
        )





@router.get("/collection/status")
async def check_collection_status():
    """Check the status of the Qdrant collection"""
    try:
        generator = MCQGenerator()
        rag = generator.rag
        
        collections = rag.qdrantClient.get_collections().collections
        collection_info = []
        
        for collection in collections:
            collection_info.append({
                "name": collection.name,
                "points_count": collection.points_count
            })
        
        all_docs = rag.retrieve_all_documents()
        
        return JSONResponse(
            content={
                "collections": collection_info,
                "total_documents_in_pdf_chunks": len(all_docs),
                "status": "healthy"
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "message": "Failed to check collection status"},
            status_code=500
        )


@router.delete("/collection/delete")
async def delete_collection(collection_name: str = "pdf_chunks"):
    """
    Delete a collection from Qdrant.
    
    Parameters:
        collection_name (str): Name of the collection to delete. Defaults to "pdf_chunks"
    """
    try:
        generator = MCQGenerator()
        rag = generator.rag
        
        success = rag.delete_collection(collection_name=collection_name)
        
        if success:
            return JSONResponse(
                content={
                    "message": f"Collection '{collection_name}' deleted successfully",
                    "collection_name": collection_name,
                    "status": "deleted"
                },
                status_code=200
            )
        else:
            return JSONResponse(
                content={
                    "error": f"Failed to delete collection '{collection_name}'",
                    "status": "failed"
                },
                status_code=400
            )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "message": "Failed to delete collection"},
            status_code=500
        )


@router.post("/collection/recreate")
async def recreate_collection(collection_name: str = "pdf_chunks"):
    """
    Recreate a collection in Qdrant.
    
    Parameters:
        collection_name (str): Name of the collection to recreate. Defaults to "pdf_chunks"
    """
    try:
        generator = MCQGenerator(collection_name=collection_name)
        rag = generator.rag
        
        success = rag.recreate_collection()
        
        if success:
            return JSONResponse(
                content={
                    "message": f"Collection '{collection_name}' recreated successfully",
                    "collection_name": collection_name,
                    "status": "created"
                },
                status_code=200
            )
        else:
            return JSONResponse(
                content={
                    "error": f"Failed to recreate collection '{collection_name}'",
                    "status": "failed"
                },
                status_code=400
            )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "message": "Failed to recreate collection"},
            status_code=500
        )

