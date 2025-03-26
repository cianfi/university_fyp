import json
import logging
import ast

from langchain_core.tools import tool
from pyats.topology import loader

logging.getLogger("unicon").setLevel(logging.ERROR)
logging.getLogger("genie").setLevel(logging.ERROR)

class ShowBGPTools():
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
        return show(device_name, "show ip bgp")
    
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
        return show(device_name, "show bgp neighbors")
    
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
        return show(device_name, "show bgp")
    
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
        return show(device_name, "show bgp summary")

class ShowOSPFTools():
    @tool
    def show_ip_ospf(device: str) -> str:
        """
        This function is used to run the 'show ip ospf' command.

        Args:
            device (str): The name of the network device.

        Returns:
            str: The output from the device.
        """
        return show(device, "show ip ospf")
    
class ShowInterfaceTools():
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
        return show(device, "show ip interface brief")
    
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
        return show(device, "show ip interface")
    
class ShowConfigurationTools():
    @tool
    def show_run(device: str) -> dict:
        """
        This function is used to run the 'show running-config' command on the network device.

        Args:
            device (str): The name of the network device. 
        
        Returns:
            dict: This will return the running configuration of the device.
        """
        return show(device, "show running-config")

class ConfigureDeviceTools():
    @tool
    def configuration(solution_configuration: str | dict) -> dict:
        """
        This function is used to configure a network device, using PyATS, with the given configuration.

        The format of configuration NEEDS to be a string which contains a dictionary.
        The dictionary needs to contain a key which is the device name, and the value 
        which is the configuration to apply to the device. Each command MUST be separated
        by a newline character. For example:
        '{"router-40": "command1\ncommand2\ncommand3..."}'

        Args:
            device_name (str): The name of the network device. 
            configuration (str): The configuration to apply to the network device.
        
        Returns:
            dict: This will return a dictionary with the status of the configuration.
        """
        if isinstance(solution_configuration, dict):
            return configure(solution_configuration)
        else:
            return configure(ast.literal_eval(solution_configuration))
    
def show(device: str, command: str) -> dict:
    testbed = loader.load("./network/testbed.yaml")

    device = testbed.devices[device]
    device.connect()

    parsed_output = device.parse(command)
    device.disconnect()

    return json.loads(json.dumps(parsed_output, indent=4))

def configure(configuration: dict) -> dict:
    testbed = loader.load("./network/testbed.yaml")
    for k,v in configuration.items():
        device = testbed.devices[k]
        device.connect()

        try:
            device.configure(v.replace("\r", ""))
            device.disconnect()
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    return {"status": "success"}