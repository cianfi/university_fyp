from netmiko import ConnectHandler

class agent_commands():
    def __init__(
            self,
            device_type: str,
            host: str,
            username: str,
            password: str):
        
        self.device = ConnectHandler(
            device_type=device_type,
            host=host,
            username=username,
            password=password
        )

    def command_show_ip_interface_brief(self) -> str:
        output: str = self.device.send_command('show ip interface brief')
        return output
        
    def command_show_ip_route(self) -> str:
        output: str = self.device.send_command('show ip route')
        return output
