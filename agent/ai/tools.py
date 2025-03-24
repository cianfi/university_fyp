import json
import logging

from langchain_core.tools import tool
from pyats.topology import loader

from .models import ConfigurationFormat

logging.getLogger("unicon").setLevel(logging.ERROR)
logging.getLogger("genie").setLevel(logging.ERROR)

class BGP():
    def show_run_section_bgp(device: str):
        return BGP._show(device, "show run | section bgp")

    def show_ip_bgp(device: str):
        return BGP._show(device, "show ip bgp")
    
    def show_bgp_neighbors(device: str):
        return BGP._show(device, "show bgp neighbors")
    
    def show_bgp(device: str):
        return BGP._show(device, "show bgp")
    
    def show_bgp_summary(device: str):
        return BGP._show(device, "show bgp summary")

    def _show(device: str, command: str):
        testbed = loader.load("./network/testbed.yaml")

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
        testbed = loader.load("./network/testbed.yaml")

        device = testbed.devices[device]
        device.connect()

        parsed_output = device.parse(command)
        device.disconnect()

        return json.dumps(parsed_output, indent=4)

class Interface():
    def show_ip_interface_brief(device: str) -> dict:
        return Interface._show(device, "show ip interface brief")
    
    def show_ip_interface(device: str) -> dict:
        return Interface._show(device, "show ip interface")


    def _show(device: str, command: str) -> dict:
        testbed = loader.load("./network/testbed.yaml")

        device = testbed.devices[device]
        device.connect()

        parsed_output = device.parse(command)
        device.disconnect()

        return json.loads(json.dumps(parsed_output, indent=4))

class Config():
    def solution_configuration(device_name: str, configuration: str) -> dict:
        return Config._configure(device_name, configuration)
    
    def _configure(device_name: str, configuration: str) -> dict:
        testbed = loader.load("./network/testbed.yaml")

        device = testbed.devices[device_name]
        device.connect()

        device.configure(configuration)
        device.disconnect()

        return {"status": "success"}

class BGPTools():
    @tool
    def show_run_section_bgp(device_name) -> str:
        """
        This function is used to run the 'show run | section bgp' command which will provide
        all of the BGP configurations within the running configuration of the given network
        device.

        Args:
            device (str): The name address of the network device. 
        
        Returns:
            str: The output from the device.
        """
        return BGP.show_run_section_bgp(device_name)

    @tool
    def show_ip_bgp(device_name) -> str:
        """
        This function is used to run the 'show ip bgp' command which will show all the bgp 
        routes on the given network device. This is useful to see where the next hop is for 
        a packet or what the BGP neighbors are sharing.

        Args:
            device (str): The name address of the network device. 
        
        Returns:
            str: The output from the device.
        """
        return BGP.show_ip_bgp(device_name)
    
    @tool
    def show_bgp_neighbors(device_name) -> str:
        """
        This function is used to run the 'show bgp neighbors' command which will show all
        the BGP neighbors connected to the given network device. This is useful to see 
        statisitical data between the choosen device and its BGP neighbors.

        Args:
            device (str): The name address of the network device. 
        
        Returns:
            str: The output from the device.
        """
        return BGP.show_bgp_neighbors(device_name)
    
    @tool
    def show_bgp(device_name) -> str:
        """
        This function is used to run the 'show bgp' command which will show if
        BGP is configured on the device.

        Args:
            device (str): The name of the network device. 
        
        Returns:
            str: The output from the device.
        """
        return BGP.show_bgp(device_name)
    
    @tool
    def show_bgp_summary(device_name) -> str:
        """
        This function is used to run the 'show bgp summary' command which will show
        a summary of the BGP configuration on the given network device.

        Args:
            device (str): The name of the network device.

        Returns:
            str: The output from the device.
        """
        return BGP.show_bgp_summary(device_name)

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
    def show_ip_interface_brief(device: str) -> dict:
        """
        This function is used to run the 'show ip interface brief' command.

        Args:
            device (str): The name of the network device. 
        
        Returns:
            This returns data in a dictionary format. 
            This tool will return ip_address, interface_is_ok, method, status and protocol for each interface.
        """
        return Interface.show_ip_interface_brief(device)
    
    @tool
    def show_ip_interface(device: str) -> dict:
        """
        This function is used to run the 'show ip interface' command. 

        Args:
            device (str): The name of the network device. 
        
        Returns:
            This returns data in a dictionary format. 
            This tool will return EVERYTHING about each interface.
        """
        return Interface.show_ip_interface(device)
    
class ConfigTools():
    @tool
    def configuration(Configuration: ConfigurationFormat) -> dict:
        """
        This function is used to configure a network device with a given configuration.

        Args:
            device_name (str): The name of the network device. 
            configuration (str): The configuration to apply to the network device.
        
        Returns:
            dict: This will return a dictionary with the status of the configuration.
        """
        return Config.solution_configuration(Configuration.device, Configuration.configuration)