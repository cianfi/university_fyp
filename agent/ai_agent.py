from langchain_core.tools import tool, render_text_description
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from ai.llm import local_llm
from ai.tools import BGPTools, Interface, OSPFTools
from ai.models import LLMQuery, LLMResponse

import argparse

class Agent:
    def __init__(self):
        self.tools = [
            show_ip_interface,
        ]

        self.template = '''
    NETWORK INSTRUCTIONS:
    You are an expert network engineer specializing in network troubleshooting.

    You will either be asked a question about a network device OR be triggered via alerts from Grafana with the alert name and device.

    From this, you will provide the user with the answer to their question or try to solve the alert that has been triggered.

    You are constantly learning and improving through every question and issue you encounter, making this a faster and more efficient process in the future.

    You are provided a list of tools that can be used to get the user information or come up with the solution to fix the issue at hand.
    
    **IMPORTANT**
    1. **If you have provided your final answer, please end.**
    2. **DO NOT re-use tools unless necessary within the same invoke chain.**
    3. **If a tool does not provide the expected output, please try another tool that you have access to.**

    **TOOLS:**  
    {tools}

    **Available Tool Names (use exactly as written):**  
    {tool_names}

    **FORMAT:**
    Thought: Do I need a tool? Yes
    Action: tool
    Action Input: device
    Observation: result

    When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
    Thought: Do I need a tool? No
    Final Answer: your final response

    Assistant has access to the following tools:
    - show_ip_interface: Executes the 'show ip interface' command on the network device and returns the parsed output.
    - show_ip_interface_brief: Executes the 'show ip interface brief' command on the network device and returns the parsed output.
    - show_bgp_neighbors: Executes the 'show bgp neighbors' command on the network device and returns the parsed output.
    - show_ip_bgp: Executes the 'show ip bgp' command on the network device and returns the parsed output.
    - show_run_section_bgp: Executes the 'show run | section bgp' command on the network device and returns the parsed output.
    - show_bgp: Executes the 'show bgp' command on the network device and returns the parsed output.
    - show_ip_ospf: Executes the 'show ip ospf' command on the network device and returns the parsed output.
    - show_run_section_ospf: Executes the 'show run | section ospf' command on the network device and returns the parsed output.

    Begin!
    New input: {input}

    {agent_scratchpad}
    '''
        self.input_variables = ['input', 'agent_scratchpad'],
        self.llm = local_llm()

    def alert(self, llm_message: LLMQuery):
        tool_description = render_text_description(self.tools)

        prompt_template: PromptTemplate = PromptTemplate(
        template=self.template,
        input_variables=self.input_variables,
        partial_variables={
            "tools": tool_description,
            "tool_names": ", ".join([t.name for t in self.tools])
        }
        )
        print(tool_description)
        print(", ".join([t.name for t in self.tools]))
        agent = create_react_agent(llm=self.llm, prompt=prompt_template, tools=self.tools)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            handle_parsing_errors=True,
            verbose=True,
            max_iterations=10
        )

        response: LLMResponse = self._llm_invoke(agent_executor, llm_message)

        return LLMResponse(input=response["input"], agent_scratchpad=response["agent_scratchpad"], output=response["output"])


    def _llm_invoke(self, agent_executor: AgentExecutor, llm_message: LLMQuery):
        """This is the function that will send the message to the llm"""
        return agent_executor.invoke(
            {
                "input": f"{llm_message.question}",
                "agent_scratchpad": ""
            }
            )


@tool
def show_ip_interface(device: str) -> dict:
    """
    This function is used to run the 'show ip interface' command. 

    Args:
        device (str): The name of the network device. 
    
    Returns:
        This returns data in a dictionary format. 
        This tool will return EVERYTHING about each interface. For example everything from the MTU to the IP address.
    """
    return Interface.show_ip_interface(device=device)

@tool  
def show_ip_interface_brief(device: str) -> dict:
    """
    This function is used to run the 'show ip interface brief' command.

    Args:
        device (str): The name of the network device. 
    
    Returns:
        This returns data in a dictionary format. 
        This tool will return ip_address, interface_is_ok, method, status and protocol for each interface.
    """
    return Interface.show_ip_interface_brief(device=device)

def main():
    parser = argparse.ArgumentParser(description='Run the AI Agent for Network Automation')
    parser.add_argument('--question', type=str, help='The question for AI Agent', required=True)
    args = parser.parse_args()

    message = LLMQuery(question=args.question)
    agent = Agent()
    print("Question: ", message.question)
    print("Response: ", agent.alert(llm_message=message).output)

if __name__ == "__main__":
    main()