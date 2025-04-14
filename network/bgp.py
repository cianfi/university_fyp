import logging

from pyats.topology import loader

logging.getLogger("unicon").setLevel(logging.ERROR)
logging.getLogger("genie").setLevel(logging.ERROR)

bgp_configuration: dict = {
    "router-1": [
        "no router ospf 1\nno router bgp 1",
        "interface GigabitEthernet2\nno ip ospf 1 area 0",
        "router bgp 1\nbgp router-id 100.100.100.1\nbgp log-neighbor-changes\nnetwork 5.5.5.0 mask 255.255.255.0\nnetwork 6.6.6.0 mask 255.255.255.0\nneighbor 100.100.100.2 remote-as 2",
    ],
    "router-2": [
        "no router ospf 1\nno router bgp 1",
        "interface GigabitEthernet2\nno ip ospf 1 area 0",
        "router bgp 2", "bgp router-id 100.100.100.2\nbgp log-neighbor-changes\nnetwork 7.7.7.0 mask 255.255.255.0\nnetwork 8.8.8.0 mask 255.255.255.0\nneighbor 100.100.100.1 remote-as 1",
    ],
}

testbed = loader.load("./agent/ai/testbed.yaml")
for device_raw in bgp_configuration:
    device = testbed.devices[device_raw]
    device.connect()

    for command in bgp_configuration[device_raw]:
        device.configure(command)
    print()
    
    device.disconnect()