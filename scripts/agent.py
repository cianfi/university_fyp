from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent
from langchain_ollama import OllamaLLM

@tools
def location() -> str:
    return 

llm = OllamaLLM(model="mistral", base_url="localhost:11434")
tools = load_tools([''], llm=llm)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    verbose=True,
    handle_parsing_errors=True
)