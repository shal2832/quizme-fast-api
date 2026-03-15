import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import SystemMessage, HumanMessage
from src.service.qdrantApiService import qdrantApiServiceInstance

def get_llm():
    """Initialize and return the LLM instance"""
    try:
        repo_id = "meta-llama/Llama-3.3-70B-Instruct"
        llm = HuggingFaceEndpoint(
            repo_id=repo_id,
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
            task="text-generation",
            temperature=0.7,
            max_new_tokens=2048
        )
        return llm
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        raise
def llm_invoke(query: str, prompt: str, invoked_by_mcqApi = False) -> str:
    """
    Invoke LLM based on user query and get reponse

    Args: 
        query: input by user,
        prompt: system_prompt for model behavior,
        invoked_by_mcqApi: boolean value to determine respective context retrieval methods

    Returns:
        Response content from llm
    """
    if(invoked_by_mcqApi):
        context_response = qdrantApiServiceInstance.entire_context_api()
        context = context_response.json().get("context", "")
        print("Entire context retrived for mcq generation")
    else:
        context_response = qdrantApiServiceInstance.query_api(query)
        context = context_response.json().get("context", "")
        print("Context retrieved based on user query")

    system_prompt = prompt.replace("{context}", context)
    try:
        print(f"Invoking LLM with prompt: {system_prompt}")
        chat = ChatHuggingFace(llm=get_llm())
        response = chat.invoke([SystemMessage(content=system_prompt),
                    HumanMessage(content=query)])  
        print(f"LLM response for query '{query}': {response.content}") 
        return str(response.content).strip() if response else ""
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        raise

