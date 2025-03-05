var = [{"device_name": "router-1", "data": {"interfaces-state": {"@xmlns": "urn:ietf:params:xml:ns:yang:ietf-interfaces", "interface": [{"name": "GigabitEthernet1", "admin-status": "up", "oper-status": "up"}, {"name": "GigabitEthernet2", "admin-status": "up", "oper-status": "up"}, {"name": "GigabitEthernet3", "admin-status": "down", "oper-status": "down"}, {"name": "GigabitEthernet4", "admin-status": "down", "oper-status": "down"}, {"name": "GigabitEthernet5", "admin-status": "down", "oper-status": "down"}, {"name": "Loopback0", "admin-status": "up", "oper-status": "up"}, {"name": "Loopback1", "admin-status": "up", "oper-status": "up"}, {"name": "Control Plane", "admin-status": "up", "oper-status": "up"}]}}}]

import json

for square in var:
    print(square["data"]["interfaces-state"])



