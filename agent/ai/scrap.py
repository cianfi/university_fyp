from langchain_core.tools import tool, render_text_description
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from pyats.topology import loader

import time

from llm import local_llm
from tools import BGPTools, OSPFTools, InterfaceTools

BGP = BGPTools()
OSPF = OSPFTools()
INTERFACE = InterfaceTools()

tools = [
    BGP.show_bgp,
    BGP.show_bgp_neighbors,
    BGP.show_ip_bgp,
    BGP.show_run_section_bgp,
    OSPF.show_ip_ospf,
    OSPF.show_run_section_ospf,
    INTERFACE.show_ip_interface,
    INTERFACE.show_ip_interface_brief,
]


template = '''
NETWORK INSTRUCTIONS:
You are an expert network engineer specializing in network troubleshooting.

You will either be asked to show something within a network device or be triggered via alerts from Grafana with the alert name and device.

From this, you will provide the user with the answer to their question or try to solve the alert that has been triggered.

You are constantly learning and improving through every question and issue you encounter, making this a faster and more efficient process in the future.

You are provided a list of tools that can be used to get the user information or come up with the solution to fix the issue at hand.

**IMPORTANT**
1. Provide the user with the answer directly. Do not expect any more user input than the question. The other input you will receive is the data from the tools.
2. Once you have given the user the answer, end the process.
3. Do not re-use tools UNLESS necessary within the same invoke chain. If the chain ends, reset this statement. For example, if you have applied configuration and want to see if it has worked.
4. Analyze output only, do not write code to extract the answer from the data. The data is returned in JSON.
5. Ensure that the device name follows the structure '[network_device]-[number]' and does NOT have anything before or after it. For example 'router-4'.

**TOOLS**
{tools}

**Available Tool names**
{tool_names}

If you want to use a tool, you MUST use the following response structure:
Thought: Do I need a tool? Yes
Action: [tool]
Action Input: [device]
Observation: [result]

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
Thought: Do I need a tool? No
Final Answer: [your final response]

**EXAMPLE**
Question: Please provide me the MTU for each interface in 'router-2'

Thought: Do I need a tool? Yes
Action: show_ip_interface
Action Input: router-2
Observation: [device data]

Thought: Do I need a tool? No
Final Answer: The MTU for each interface in 'router-2' is:
* GigabitEthernet1: 1500
* GigabitEthernet2: N/A
* GigabitEthernet3: N/A
* GigabitEthernet4: 1500
* Loopback0: 1514
* Loopback1: 1514


Correct Formatting is Essential: Ensure that every response follows the format strictly to avoid errors.

**BEGIN**
Please begin!

Alert or question: {input}

{agent_scratchpad}
'''

tool_description = render_text_description(tools)

input_variables = ['input', 'agent_scratchpad']

prompt_template = PromptTemplate(
    template=template,
    input_variables=input_variables,
    partial_variables={
        "tools": tool_description,
        "tool_names": ", ".join([t.name for t in tools])
    }
)

llm = local_llm()

agent = create_react_agent(llm, tools, prompt_template)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    verbose=True,
    max_iterations=10
)

start_time = time.time()
agent_executor.invoke({
    "input": "Please provide me the MTU for each interface in 'router-2'",
    "agent_scratchpad": ""
})
end_time = time.time()
total_time = end_time - start_time
print(f"TOTAL TIME TAKEN: {total_time}")