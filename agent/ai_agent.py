from langchain_core.tools import render_text_description
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from ai.llm import local_llm
from ai.prompt import promt_template
from ai.tools import ShowBGPTools, ShowConfigurationTools, ConfigureDeviceTools, ShowInterfaceTools
from ai.models import LLMResponse

import argparse

class Agent:
    def __init__(self):
        self.tools = [
            ShowBGPTools.show_ip_bgp,
            ShowBGPTools.show_bgp_neighbors,
            ShowBGPTools.show_bgp_summary,
            ShowConfigurationTools.show_run,
            ConfigureDeviceTools.configuration,
            ShowInterfaceTools.show_ip_interface,
            ShowInterfaceTools.show_ip_interface_brief
        ]

        self.template = promt_template
        self.input_variables = ['input', 'agent_scratchpad'],
        self.llm = local_llm()

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

        alert_description += " Use provided tools to figure out (A) what the issue is (B) check running configuration to verfiy (C) the configuration needed for the fix (D) implement the fix using the configuration tool."
        
        print(alert_description)

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