import json

from langchain_core.tools import tool
from pyats.topology import loader


class BGP():
    def show_run_section_bgp(device: str):
        return BGP._show(device, "show run | section bgp")

    def show_ip_bgp(device: str):
        return BGP._show(device, "show ip bgp")

    def _show(device: str, command: str):
        testbed = loader.load("./llm/network/testbed.yaml")

        device = testbed.devices[device]
        device.connect()

        parsed_output = device.parse(command)
        device.disconnect()

        return json.dumps(parsed_output, indent=4)


class OSPF():
    def show_run_section_ospf(device: str) -> str:
        return OSPF._show(device, "show run | section ospf")

    def show_ip_ospf(device: str) -> str:
        return OSPF._show(device, "show ip ospf")

    def _show(device: str, command: str) -> str:
        testbed = loader.load("./llm/network/testbed.yaml")

        device = testbed.devices[device]
        device.connect()

        parsed_output = device.parse(command)
        device.disconnect()

        return json.dumps(parsed_output, indent=4)

class Interface():
    def show_ip_interface_brief(device: str) -> str:
        return Interface._show(device, "show ip interface brief")
    
    def show_ip_interface(device: str) -> str:
        return Interface._show(device, "show ip interface")


    def _show(device: str, command: str) -> str:
        testbed = loader.load("./llm/network/testbed.yaml")

        device = testbed.devices[device]
        device.connect()

        parsed_output = device.parse(command)
        device.disconnect()

        return json.dumps(parsed_output, indent=4)


class BGPTools():
    @tool
    def show_run_section_bgp(device: str) -> str:
        """TEST"""
        return BGP.show_run_section_bgp(device)

    @tool
    def show_ip_bgp(device: str) -> str:
        """TEST"""
        return BGP.show_ip_bgp(device)


class OSPFTools():
    @tool
    def show_run_section_ospf(device: str) -> str:
        """TEST"""
        return OSPF.show_run_section_ospf(device)

    @tool
    def show_ip_ospf(device: str) -> str:
        """TEST"""
        return OSPF.show_ip_ospf(device)
    
class InterfaceTools():
    @tool
    def show_ip_interface_brief(device: str) -> str:
        """TEST"""
        return Interface.show_ip_interface_brief(device)
    
    @tool
    def show_ip_interface(device: str) -> str:
        """TEST"""
        return Interface.show_ip_interface(device)