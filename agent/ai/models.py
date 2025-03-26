from dataclasses import dataclass

@dataclass
class LLMResponse:
    input: str
    agent_scratchpad: str
    output: str
