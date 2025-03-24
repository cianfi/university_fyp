from dataclasses import dataclass

@dataclass
class LLMQuery:
    question: str

@dataclass
class LLMResponse:
    input: str
    agent_scratchpad: str
    output: str