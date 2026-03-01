import os

def get_llm():
    """Initialize and return the LLM instance"""
    try:
        from langchain_huggingface import HuggingFaceEndpoint
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



def llm_invoke(prompt: str, system_prompt: str = "You are helpful.") -> str:
    """Invoke the LLM with a prompt"""
    try:
        from langchain_huggingface import ChatHuggingFace
        from langchain_core.messages import SystemMessage, HumanMessage
        print(f"Invoking LLM with prompt: {prompt}")
        chat = ChatHuggingFace(llm=get_llm())
        resp = chat.invoke([SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)])   
        return str(resp.content).strip() if resp else ""
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        raise

