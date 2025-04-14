from langchain_core.tools import render_text_description
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from ai.llm import local_llm
from ai.prompt import prompt_template
from ai.tools import ShowBGPTools, ShowConfigurationTools, ConfigureDeviceTools, ShowInterfaceTools, ShowOSPFTools
from ai.models import LLMResponse

import argparse
import time

class Agent:
    def __init__(self):
        self.tools = [
            ShowBGPTools.show_ip_bgp,
            ShowBGPTools.show_bgp_neighbors,
            ShowBGPTools.show_bgp_summary,
            ShowConfigurationTools.show_run,
            ConfigureDeviceTools.configuration,
            ShowInterfaceTools.show_ip_interface,
            ShowInterfaceTools.show_ip_interface_brief,
            ShowOSPFTools.show_ip_ospf,
            ShowOSPFTools.show_ip_ospf_neighbors,
            ShowOSPFTools.show_ip_ospf_database,
            ShowOSPFTools.show_ip_ospf_interface,
        ]

        self.prompt = prompt_template
        self.input_variables = ['input', 'agent_scratchpad'],
        self.llm = local_llm()

    def alert(self, alert_description: str) -> LLMResponse:
        """
        This is the function that will start the whole AI Agent process.
        
        arg:
            alert_description: str: The alert description that will be sent to the llm

        return:
            LLMResponse: The response from the llm
        """
        tool_description = render_text_description(self.tools)

        prompt_template: PromptTemplate = PromptTemplate(
        template=self.prompt,
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
            max_iterations=10,
        )

        print(alert_description)
        alert_description += " Use provided tools to figure out (A) what the issue is (B) check running configuration to verfiy (C) the configuration needed for the fix (D) implement the fix using the configuration tool."

        start_time = time.time()
        response: LLMResponse = self._llm_invoke(agent_executor, alert_description)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

        return LLMResponse(input=response["input"], agent_scratchpad=response["agent_scratchpad"], output=response["output"])

    def _llm_invoke(self, agent_executor: AgentExecutor, llm_message: str) -> AgentExecutor:
        """
        This is the function that will send the message to the llm
        
        arg:
            agent_executor: AgentExecutor: The agent executor that will be used to send the message to the llm
            llm_message: str: The message that will be sent to the llm
            
        return:
            LLMResponse: The response from the llm
        """
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