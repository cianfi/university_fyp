import json
import logging

from pyats.topology import loader

logging.getLogger("unicon").setLevel(logging.ERROR)
logging.getLogger("genie").setLevel(logging.ERROR)

basic_configuration: dict = {
    "router-1": [
        "interface g2",
        "desc Interface to Router-2",
        "ip address 100.100.100.1 255.255.255.252",
        "no shut",
        "int lo0",
        "ip address 5.5.5.1 255.255.255.0 ",
        "no shut",
        "int lo1",
        "ip address 6.6.6.1 255.255.255.0",
        "no shut",
    ],
    "router-2": [
        "interface g2",
        "desc Interface to Router-1",
        "ip address 100.100.100.2 255.255.255.252",
        "no shut",
        "int lo0",
        "ip address 7.7.7.1 255.255.255.0 ",
        "no shut",
        "int lo1",
        "ip address 8.8.8.1 255.255.255.0",
        "no shut",
    ],
}


testbed = loader.load("./network/testbed.yaml")
for device in basic_configuration:
    device = testbed.devices[device]
    device.connect()

    for command in basic_configuration[device]:
        device.parse(command)
    
    device.disconnect()

