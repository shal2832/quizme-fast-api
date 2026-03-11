from fastapi import APIRouter , UploadFile
from fastapi.responses import JSONResponse
from src.models.llama3 import llm_invoke
from src.service.processFile import chunk_file
from src.service.prepareMCQ import mcq_generator
from src.service.qdrantApiService import qdrantApiServiceInstance
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
    temp_file_path, serializable_chunks = chunk_file(data, file.filename)
    #delete the temp file after processing
    os.remove(temp_file_path)
    return JSONResponse(content={"message": "File processed successfully", "file" : temp_file_path, "number of chunks": serializable_chunks}, status_code=200)

@router.post('/query')
def chat_with_llm(prompt: str):
    """
    Endpoint to handle queries to the LLM. It takes a prompt as input, retrieves relevant context, and returns the LLM's response.
    
    Args:
        prompt (str): The query or prompt to be sent to the LLM.

    Returns:
        JSONResponse: A response containing the LLM's answer to the query.
    """
    system_prompt = f"""
    You are a encylopidea based on the retrieved context
    Always be in context, and be conversational with the user.
    Use the provided context to answer the user's query. If the context does not contain the answer, respond with "I don't know".
    Content: {{context}}
    """
    res =  llm_invoke(prompt, system_prompt, False)
    return JSONResponse(content={"message": res}, status_code=200)

@router.post('/generate-mcq/context')
def generate_mcq(num_of_questions : int = 5, query: str = ""):
    """
    Endpoint to generate multiple choice questions (MCQs) based on available context. It uses the LLM to create educational and relevant MCQs.
    
    Args:
        prompt (str): The content or topic for which MCQs need to be generated.

    Returns:
        JSONResponse: A response containing the generated MCQs in JSON format.
    """
  
    mcq_json = mcq_generator.generate_mcq_with_context(num_of_questions,query )
    return JSONResponse(content={"message" : mcq_json}, status_code=200)


@router.post('/generate-mcq/all')
def generate_mcq(num_of_questions : int = 5):
    """
    Endpoint to generate multiple choice questions (MCQs) based on all documents. It uses the LLM to create educational and relevant MCQs.
    
    Args:
        prompt (str): The content or topic for which MCQs need to be generated.

    Returns:
        JSONResponse: A response containing the generated MCQs in JSON format.
    """
  
    mcq_json = mcq_generator.generate_mcq_with_context(num_of_questions)
    return JSONResponse(content={"message" : mcq_json}, status_code=200)



@router.delete('/collection/delete')
def delete_collection(collection_name):
    """
    Endpoint to delete the existing collection in Qdrant. This can be used to clear all stored data and start fresh.
    """
    response = qdrantApiServiceInstance.delete_api(collection_name)
    return JSONResponse(content={"message" : "Collection deleted successfully"}, status_code=response.status_code)

