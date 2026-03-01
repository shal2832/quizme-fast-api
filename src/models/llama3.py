import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import SystemMessage, HumanMessage
from src.service.rag import Rag

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



def llm_invoke(query: str) -> str:
    """Invoke the LLM with a prompt"""
    context = Rag().context_retrieval(query)
    print(f"Context retrieved for query '{query}': {context}")

    system_prompt = f"""
    You are a questioner, based on the retreived context, 
    prepare mutiple choice questions and interact with the user on the follow ups.

    Always be in context, and be conversational with the user.
    Use the provided context to answer the user's query. If the context does not contain the answer, respond with "I don't know".
    Context: {context}
    """
    try:
        print(f"Invoking LLM with prompt: {query}")
        chat = ChatHuggingFace(llm=get_llm())
        resp = chat.invoke([SystemMessage(content=system_prompt),
                    HumanMessage(content=query)])   
        return str(resp.content).strip() if resp else ""
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        raise

