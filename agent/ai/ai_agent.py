from network.tools import BGPTools, OSPFTools, InterfaceTools

from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool, render_text_description
from langchain_community.llms import ollama
from langgraph.prebuilt import create_react_agent

import json

def alert():
    pass

def main():
    llm = ollama(
        model="phi3:mini",
        base_url="http://127.0.0.1:11434",
    )

    tools: list[function] = [
        BGPTools.show_run_section_bgp,
        BGPTools.show_ip_bgp,
        OSPFTools.show_run_section_ospf,
        OSPFTools.show_ip_ospf,
        InterfaceTools.show_ip_interface_brief,
        InterfaceTools.show_ip_interface,
    ]

    tool_description = render_text_description(tools)

# Need to read up on best templates
template = """

"""

input_variables: list[str] = [
    "input",
    "tools",
    "tool_names",
    "agent_scratchpad",
    "chat_history"
]

