test = {
    "rpc-reply": {
        "@xmlns": "urn:ietf:params:xml:ns:netconf:base:1.0",
        "@message-id": "urn:uuid:9be31f6d-5060-4e46-a40c-fee48e43b766",
        "@xmlns:nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
        "data": {
            "interfaces-state": {
                "@xmlns": "urn:ietf:params:xml:ns:yang:ietf-interfaces",
                "interface": [
                    {
                        "name": "GigabitEthernet1",
                        "admin-status": "up",
                        "oper-status": "up"
                    },
                    {
                        "name": "GigabitEthernet2",
                        "admin-status": "up",
                        "oper-status": "up"
                    },
                    {
                        "name": "GigabitEthernet3",
                        "admin-status": "down",
                        "oper-status": "down"
                    },
                    {
                        "name": "GigabitEthernet4",
                        "admin-status": "down",
                        "oper-status": "down"
                    },
                    {
                        "name": "GigabitEthernet5",
                        "admin-status": "down",
                        "oper-status": "down"
                    },
                    {
                        "name": "Loopback0",
                        "admin-status": "up",
                        "oper-status": "up"
                    },
                    {
                        "name": "Loopback1",
                        "admin-status": "up",
                        "oper-status": "up"
                    },
                    {
                        "name": "Control Plane",
                        "admin-status": "up",
                        "oper-status": "up"
                    }
                ]
            }
        }
    }
}

print(test["rpc-reply"])