from langchain_ollama import ChatOllama

def local_llm(model:str="llama3.2:3b", base_url:str="http://127.0.0.1:11434") -> ChatOllama:
    """
    This is the LLM configured to use Ollama locally.
    This returns OllamaLLM()
    """
    return ChatOllama(
        model=model,
        base_url=base_url,
        temperature=0.1,
        num_ctx=8000,
    )