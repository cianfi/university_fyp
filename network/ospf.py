import json
import logging

from pyats.topology import loader

logging.getLogger("unicon").setLevel(logging.ERROR)
logging.getLogger("genie").setLevel(logging.ERROR)

ospf_configuration: dict = {
    "router-1": [
        "no router ospf 1",
        "no router bgp 1",
        "router ospf 1",
        "network 5.5.5.0 0.0.0.255 area 0", 
        "network 6.6.6.0 0.0.0.255 area 0", 
        "network 100.100.100.0 0.0.0.3 area 0",
        "interface GigabitEthernet2",
        "ip ospf 1 area 0",
    ],
    "router-2": [
        "no router ospf 1",
        "no router bgp 1",
        "router ospf 1",
        "network 7.7.7.0 0.0.0.255 area 0", 
        "network 8.8.8.0 0.0.0.255 area 0", 
        "network 100.100.100.0 0.0.0.3 area 0",
        "interface GigabitEthernet2",
        "ip ospf 1 area 0",
    ],
}

testbed = loader.load("./network/testbed.yaml")
for device in ospf_configuration:
    device = testbed.devices[device]
    device.connect()

    for command in ospf_configuration[device]:
        device.parse(command)
    
    device.disconnect()