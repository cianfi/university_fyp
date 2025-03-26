from langchain_core.tools import tool, render_text_description
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from ai.llm import local_llm
from ai.tools import ShowBGPTools, ShowConfigurationTools, ConfigureDeviceTools, ShowInterfaceTools
from ai.models import LLMResponse

import argparse

class Agent:
    def __init__(self):
        self.tools = [
            ShowBGPTools.show_ip_bgp,
            ShowBGPTools.show_bgp_neighbors,
            ShowBGPTools.show_bgp,
            ShowBGPTools.show_bgp_summary,
            ShowConfigurationTools.show_run,
            ConfigureDeviceTools.configuration,
            ShowInterfaceTools.show_ip_interface,
            ShowInterfaceTools.show_ip_interface_brief
        ]

        self.template = '''
    NETWORK INSTRUCTIONS:
    You are an expert network engineer specializing in network troubleshooting.

    You will either be asked a question about a network device OR be triggered via alerts from Grafana with the alert name and device.

    If the user asks a question, use your tools to give them the answer.

    If an alert is triggered, you will be given the alert description and device. You will need to use your tools to analyse the device and solve the issue with the configuration tool.

    There should always be some type of routing connectivity between router-1 and router-2 if it is BGP or OSPF. Nothing else. 

    You are constantly learning and improving through every question and issue you encounter, making this a faster and more efficient process in the future.

    If you know the fix to the issued alert, configure the device with the fix using the configuration tool. Ensure that when calling the configuration tool, you use the device name as the key and the configuration as the value and encapsulate this dictionary within a string.

     **IMPORTANT**
    1. **If you have provided your final answer, please end.**
    2. **DO NOT re-use tools**
    3. **If a tool does not provide the expected output, please try another tool that you have access to.**
    4. **If you know the fix to the issue, please use the configuration tool to configure the device.**
    5. **If you have provided the fix, please end.**
    
    **TOOLS:**  
    {tools}

    **Available Tool Names (use exactly as written):**  
    {tool_names}

    **FORMAT:**
    If you need to use a tool, you MUST use the format:
    Thought: Do I need a tool? Yes
    Action: tool
    Action Input: device
    Observation: result

    If you need to use the configuration tool, you MUST use the format:
    Thought: Do I need a tool? Yes
    Action: configuration
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
    - show_bgp_summary: Executes the 'show bgp summary' command on the network device and returns the parsed output.
    - show_bgp: Executes the 'show bgp' command on the network device and returns the parsed output.
    - show_run: Executes the 'show run' command on the network device and returns the parsed output.
    - configuration: Configures the network device with the provided configuration and returns the parsed output. The parameter for this is a string that contains a dictionary. The device name is the key. The configuration is the value. Configuation is formatted like so: "command1\ncommand2\ncommand3...". Example {{"router-20": "command1\ncommand2\ncommand3"}}

    Begin!
    New input: {input}

    {agent_scratchpad}
    '''
        self.input_variables = ['input', 'agent_scratchpad'],
        self.llm = local_llm("llama3.1:8b")

    def alert(self, alert_description: str):
        tool_description = render_text_description(self.tools)

        # print("Alert Description: ", alert_description)

        prompt_template: PromptTemplate = PromptTemplate(
        template=self.template,
        input_variables=self.input_variables,
        partial_variables={
            "tools": tool_description,
            "tool_names": ", ".join([t.name for t in self.tools])
        }
        )
        agent = create_react_agent(llm=self.llm, prompt=prompt_template, tools=self.tools)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            handle_parsing_errors=True,
            verbose=True,
            max_iterations=10
        )

        response: LLMResponse = self._llm_invoke(agent_executor, alert_description)

        return LLMResponse(input=response["input"], agent_scratchpad=response["agent_scratchpad"], output=response["output"])

    def _llm_invoke(self, agent_executor: AgentExecutor, llm_message: str):
        """This is the function that will send the message to the llm"""
        return agent_executor.invoke(
            {
                "input": f"{llm_message}",
                "agent_scratchpad": ""
            }
            )


def main():
    parser = argparse.ArgumentParser(description='Run the AI Agent for Network Automation')
    parser.add_argument('--question', type=str, help='The question for AI Agent', required=True)
    args = parser.parse_args()

    agent = Agent()
    print("Response: ", agent.alert(alert_description=args.question).output)

if __name__ == "__main__":
    main()