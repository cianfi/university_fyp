from agent_commands import agent_commands
import requests
import json
from datetime import datetime

test = agent_commands(device_type="cisco_ios", host="devnetsandboxiosxe.cisco.com" ,username="admin", password="C1sco12345")
response = test.command_show_ip_interface_brief()

start = datetime.now()
msg = requests.request(
    method="POST",
    url="http://localhost:11434/api/generate",
    headers={
        "Content-Type": "application/json"
    },
    json={
        "prompt": f"Please tell me how many loopbacks are in the following interface brief?\n{response}",
        "stream": False,
        "model": "mistral",
    },
    verify=False
)
end = datetime.now()

total = end - start

print(msg.text)
print(total)
# curl -X POST localhost:11434/api/generate -H "Content-Type: application/json" -d '{"prompt": "hello", "stream": false, "model": "mistral"}'