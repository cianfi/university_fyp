from dataclasses import dataclass

@dataclass
class LLMQuery:
    question: str | dict

@dataclass
class LLMResponse:
    input: str
    agent_scratchpad: str
    output: str

@dataclass
class ConfigurationFormat:
    device: str
    configuration: str