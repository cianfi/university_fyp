import threading
import dataclasses

def hello():
    print("Hello")

def hello1():
    print("Hello1")

def hello2():
    print("Hello2")

def main():
    hello()
    hello1()
    hello2()
    threading.Timer(5, main).start()

def influx_client():
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    import os
 
    client = InfluxDBClient(url="http://127.0.0.1:8086", token=os.environ.get("INFLUXDB_TOKEN"), org="my-org")
    # write_api = client.write_api(write_options=SYNCHRONOUS)

    # p = Point("my_measurement").tag("location", "Prague").field("temp", 25.3)
    # write_api.write(bucket="network-data", record=p)

    query_api = client.query_api()
    tables = query_api.query('from(bucket:"network-data") |> range(start: -5m)')

    for table in tables:
        print(table.records)
        for row in table.records:
            print(row)
        print("\n\n\n")


def rows():
    # This is an example query from influxDB without flags field
    var = [
    {'result': '_result', 'table': 1, '_start': datetime.datetime(2025, 3, 5, 17, 46, 30, 136539, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 3, 5, 17, 56, 30, 136539, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 3, 5, 17, 53, 51, 979271, tzinfo=datetime.timezone.utc), '_value': 25.3, '_field': 'temp', '_measurement': 'my_measurement', 'location': 'Prague'},
    {'result': '_result', 'table': 1, '_start': datetime.datetime(2025, 3, 5, 17, 46, 30, 136539, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 3, 5, 17, 56, 30, 136539, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 3, 5, 17, 55, 36, 857771, tzinfo=datetime.timezone.utc), '_value': 25.3, '_field': 'temp', '_measurement': 'my_measurement', 'location': 'Prague'},
    {'result': '_result', 'table': 1, '_start': datetime.datetime(2025, 3, 5, 17, 46, 30, 136539, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 3, 5, 17, 56, 30, 136539, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 3, 5, 17, 56, 2, 343609, tzinfo=datetime.timezone.utc), '_value': 25.3, '_field': 'temp', '_measurement': 'my_measurement', 'location': 'Prague'},
    ]

    # This is an example query from influxDB with flags field
    var2 = [
    {'result': '_result', 'table': 0, '_start': datetime.datetime(2025, 3, 5, 17, 46, 30, 136539, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 3, 5, 17, 56, 30, 136539, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 3, 5, 17, 55, 36, 857771, tzinfo=datetime.timezone.utc), '_value': 'blue', '_field': 'flag', '_measurement': 'my_measurement', 'location': 'Prague'},
    {'result': '_result', 'table': 0, '_start': datetime.datetime(2025, 3, 5, 17, 46, 30, 136539, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 3, 5, 17, 56, 30, 136539, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 3, 5, 17, 56, 2, 343609, tzinfo=datetime.timezone.utc), '_value': 'blue', '_field': 'flag', '_measurement': 'my_measurement', 'location': 'Prague'},
    ]

    # So, adding .field() after each entry will not work. 
    

def influxdb_format() -> str:
    """InfluxDB requires payloads to be in 'line protocol' format. This function will transform
    the data dictionary to line protocol, ready to be sent off for InfludDB."""
    test = [{
                        "measurement": "measurement_test",
                        "tags": {
                            "device_name": "name_test",
                            "interface_name": "int_test",
                        },
                        "fields": {
                            "admin_status": "admin_test",
                            "oper_status": "oper_test"
                        },
                    }]
    telegraf_line_protocol = _interface_status_line_protocol(test)
    return telegraf_line_protocol
    

def _interface_status_line_protocol(telegraf_dict) -> list[str]:
    telegraf_line_protocol: list[str] = []
    
    for mtf in telegraf_dict:
        line_protocol_tags = ",".join(f"{k}={v}" for k,v in mtf["tags"].items())
        line_protocol_fields = ",".join(f'{k}="{v}"' for k,v in mtf["fields"].items())

        line_protocol_entry = f"{mtf['measurement']}"
        line_protocol_entry += f",{line_protocol_tags}"
        line_protocol_entry += f" {line_protocol_fields}"
        telegraf_line_protocol.append(line_protocol_entry)

    return telegraf_line_protocol


def influxdb_write(telegraf_line_protocol):
    import requests
    import os

    payload = "\n".join(telegraf_line_protocol)

    data = requests.request(
        "POST",
        url="http://127.0.0.1:8086/api/v2/write",
        headers={
            "Accept": "application/json",
            "Content-Type": "text/plain",
            "Authorization": f"Token {os.environ.get('INFLUXDB_TOKEN')}",
        },
        params={
            "bucket": "network-data",
            "org": "my-org",
        },
        data=payload,
        verify=False
    )

    print(data.status_code)
    print(data.text)


@dataclasses.dataclass
class ReplyData:
    device_name: str
    reply: dict


def format(): 
    var = ReplyData(device_name='router-1', reply={'interfaces-state': {'@xmlns': 'urn:ietf:params:xml:ns:yang:ietf-interfaces', 'interface': [{'name': 'GigabitEthernet1', 'admin-status': 'up', 'oper-status': 'up'}, {'name': 'GigabitEthernet2', 'admin-status': 'up', 'oper-status': 'up'}, {'name': 'GigabitEthernet3', 'admin-status': 'down', 'oper-status': 'down'}, {'name': 'GigabitEthernet4', 'admin-status': 'down', 'oper-status': 'down'}, {'name': 'GigabitEthernet5', 'admin-status': 'down', 'oper-status': 'down'}, {'name': 'Loopback0', 'admin-status': 'up', 'oper-status': 'up'}, {'name': 'Loopback1', 'admin-status': 'up', 'oper-status': 'up'}, {'name': 'Control Plane', 'admin-status': 'up', 'oper-status': 'up'}]}})
    
    for x in var.reply:
        print(var.reply[x]['interface'])


def entry():
    var = ['interface_status,device_name=router-1,interface_name=GigabitEthernet1 admin_status="up",oper_status="up"', 'interface_status,device_name=router-1,interface_name=GigabitEthernet2 admin_status="up",oper_status="up"', 'interface_status,device_name=router-1,interface_name=GigabitEthernet3 admin_status="down",oper_status="down"', 'interface_status,device_name=router-1,interface_name=GigabitEthernet4 admin_status="down",oper_status="down"', 'interface_status,device_name=router-1,interface_name=GigabitEthernet5 admin_status="down",oper_status="down"', 'interface_status,device_name=router-1,interface_name=Loopback0 admin_status="up",oper_status="up"', 'interface_status,device_name=router-1,interface_name=Loopback1 admin_status="up",oper_status="up"', 'interface_status,device_name=router-1,interface_name=Control Plane admin_status="up",oper_status="up"']

    for entry in var:
        if "Control Plane" in entry:
            var.remove(entry)


    payload = ""
    counter = 0

    while counter < len(var):
        if counter != 0:
            payload += f"\n{var[counter]}"
        else:
            payload += f"{var[counter]}"
        counter += 1
    print(payload)

def statistics_see():
    import json
    var = {'name': 'GigabitEthernet1', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'admin-status': 'up', 'oper-status': 'up', 'last-change': '2025-02-24T19:15:48.000323+00:00', 'if-index': '1', 'phys-address': 'bc:24:11:e5:1a:b7', 'speed': '102400000', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000896+00:00', 'in-octets': '3797866', 'in-unicast-pkts': '43366', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '17978725', 'out-unicast-pkts': '44789', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}
    print(json.dumps(var, indent=4))

import json

def bgp_status_data():
    var = {'rpc-reply': {'@xmlns': 'urn:ietf:params:xml:ns:netconf:base:1.0', '@message-id': 'urn:uuid:3b356207-070f-491c-a28e-86b260bd9005', '@xmlns:nc': 'urn:ietf:params:xml:ns:netconf:base:1.0', 'data': {'bgp-state-data': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-bgp-oper', 'neighbors': {'neighbor': {'afi-safi': 'ipv4-unicast', 'vrf-name': 'default', 'neighbor-id': '20.20.30.3', 'description': None, 'bgp-version': '4', 'link': 'external', 'up-time': '1w0d', 'last-write': '00:00:37', 'last-read': '00:00:06', 'installed-prefixes': '2', 'session-state': 'fsm-established', 'negotiated-keepalive-timers': {'hold-time': '180', 'keepalive-interval': '60'}, 'negotiated-cap': ['Route refresh: advertised and received(new)', 'Four-octets ASN Capability: advertised and received', 'Address family IPv4 Unicast: advertised and received', 'Enhanced Refresh Capability: advertised and received', 'Multisession Capability:', 'Stateful switchover support enabled: NO for session 1'], 'bgp-neighbor-counters': {'sent': {'opens': '1', 'updates': '2', 'notifications': '0', 'keepalives': '12343', 'route-refreshes': '0'}, 'received': {'opens': '1', 'updates': '3', 'notifications': '0', 'keepalives': '12347', 'route-refreshes': '0'}, 'inq-depth': '0', 'outq-depth': '0'}, 'connection': {'state': 'established', 'mode': 'mode-active', 'total-established': '1', 'total-dropped': '0', 'last-reset': 'never', 'reset-reason': None}, 'transport': {'path-mtu-discovery': 'true', 'local-port': '24088', 'local-host': '20.20.30.2', 'foreign-port': '179', 'foreign-host': '20.20.30.3', 'mss': '1460'}, 'prefix-activity': {'sent': {'current-prefixes': '2', 'total-prefixes': '2', 'implicit-withdraw': '0', 'explicit-withdraw': '0', 'bestpaths': '0', 'multipaths': '0'}, 'received': {'current-prefixes': '2', 'total-prefixes': '2', 'implicit-withdraw': '0', 'explicit-withdraw': '0', 'bestpaths': '2', 'multipaths': '0'}}, 'as': '2'}}}}}}
    bgp_status_filter(var)


def bgp_status_filter(data):
    # print(json.dumps(data["rpc-reply"]["data"]["bgp-state-data"]["neighbors"], indent=4))
    short = data["rpc-reply"]["data"]["bgp-state-data"]["neighbors"]
    for bgp_neighbor in short:
        print(short[bgp_neighbor]["connection"]["state"])

def bgp_test():
    var = [{'afi-safi': 'ipv4-unicast', 'vrf-name': 'default', 'neighbor-id': '20.20.20.3', 'description': None, 'bgp-version': '4', 'link': 'external', 'up-time': None, 'last-write': None, 'last-read': None, 'installed-prefixes': '0', 'session-state': 'fsm-idle', 'negotiated-keepalive-timers': {'hold-time': '0', 'keepalive-interval': '0'}, 'bgp-neighbor-counters': {'sent': {'opens': '0', 'updates': '0', 'notifications': '0', 'keepalives': '0', 'route-refreshes': '0'}, 'received': {'opens': '0', 'updates': '0', 'notifications': '0', 'keepalives': '0', 'route-refreshes': '0'}, 'inq-depth': '0', 'outq-depth': '0'}, 'connection': {'state': 'closed', 'mode': 'mode-active', 'total-established': '0', 'total-dropped': '0', 'last-reset': 'never', 'reset-reason': None}, 'transport': {'path-mtu-discovery': 'true', 'local-port': '0', 'foreign-port': '0', 'mss': '0'}, 'prefix-activity': {'sent': {'current-prefixes': '0', 'total-prefixes': '0', 'implicit-withdraw': '0', 'explicit-withdraw': '0', 'bestpaths': '0', 'multipaths': '0'}, 'received': {'current-prefixes': '0', 'total-prefixes': '0', 'implicit-withdraw': '0', 'explicit-withdraw': '0', 'bestpaths': '0', 'multipaths': '0'}}, 'as': '2'}, {'afi-safi': 'ipv4-unicast', 'vrf-name': 'default', 'neighbor-id': '20.20.30.3', 'description': None, 'bgp-version': '4', 'link': 'external', 'up-time': '00:00:33', 'last-write': '00:00:01', 'last-read': '00:00:33', 'installed-prefixes': '2', 'session-state': 'fsm-established', 'negotiated-keepalive-timers': {'hold-time': '180', 'keepalive-interval': '60'}, 'negotiated-cap': ['Route refresh: advertised and received(new)', 'Four-octets ASN Capability: advertised and received', 'Address family IPv4 Unicast: advertised and received', 'Enhanced Refresh Capability: advertised and received', 'Multisession Capability:', 'Stateful switchover support enabled: NO for session 1'], 'bgp-neighbor-counters': {'sent': {'opens': '1', 'updates': '2', 'notifications': '0', 'keepalives': '2', 'route-refreshes': '0'}, 'received': {'opens': '1', 'updates': '2', 'notifications': '0', 'keepalives': '2', 'route-refreshes': '0'}, 'inq-depth': '0', 'outq-depth': '0'}, 'connection': {'state': 'established', 'mode': 'mode-active', 'total-established': '3', 'total-dropped': '2', 'last-reset': '00:00:34', 'reset-reason': 'Router ID changed'}, 'transport': {'path-mtu-discovery': 'true', 'local-port': '41852', 'local-host': '20.20.30.2', 'foreign-port': '179', 'foreign-host': '20.20.30.3', 'mss': '1460'}, 'prefix-activity': {'sent': {'current-prefixes': '2', 'total-prefixes': '2', 'implicit-withdraw': '0', 'explicit-withdraw': '0', 'bestpaths': '0', 'multipaths': '0'}, 'received': {'current-prefixes': '2', 'total-prefixes': '2', 'implicit-withdraw': '0', 'explicit-withdraw': '0', 'bestpaths': '2', 'multipaths': '0'}}, 'as': '2'}]
    print(json.dumps(var, indent=4))

def hsrp():
    var = {'native': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-native', 'interface': {'GigabitEthernet': [{'name': '1', 'description': "'Uplink interface to ISP'", 'bandwidth': {'kilobits': '100000'}, 'ip': {'address': {'primary': {'address': '20.20.30.2', 'mask': '255.255.255.0'}}}, 'mop': {'enabled': 'false', 'sysid': 'false'}, 'negotiation': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet', 'auto': 'true'}}, {'name': '2', 'ip': {'address': {'primary': {'address': '100.100.100.2', 'mask': '255.255.255.0'}}}, 'mop': {'enabled': 'false', 'sysid': 'false'}, 'standby': {'standby-list': [{'group-number': '0', 'ip': {'address': '100.100.100.1'}, 'preempt': None, 'priority': '200'}, {'group-number': '1', 'preempt': None, 'priority': '105'}]}, 'negotiation': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet', 'auto': 'true'}}, {'name': '3', 'shutdown': None, 'mop': {'enabled': 'false', 'sysid': 'false'}, 'negotiation': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet', 'auto': 'true'}}, {'name': '4', 'shutdown': None, 'mop': {'enabled': 'false', 'sysid': 'false'}, 'negotiation': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet', 'auto': 'true'}}, {'name': '5', 'shutdown': None, 'mop': {'enabled': 'false', 'sysid': 'false'}, 'negotiation': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet', 'auto': 'true'}}], 'Loopback': [{'name': '0', 'ip': {'address': {'primary': {'address': '5.5.5.1', 'mask': '255.255.255.0'}}}}, {'name': '1', 'ip': {'address': {'primary': {'address': '6.6.6.1', 'mask': '255.255.255.0'}}}}]}}}
    print(json.dumps(var, indent=4))

def compat():
    from ncclient import manager

    host = "20.20.30.2"
    port = 830
    username = "admin"
    password = "admin"

    with manager.connect(
        host=host, port=port, username=username, password=password, hostkey_verify=False
    ) as m:
        for capability in m.server_capabilities:
            print(capability)

def ospf():
        var = {'ospf-oper-data': {'@xmlns': 'http://cisco.com/ns/yang/Cisco-IOS-XE-ospf-oper', 'ospf-state': {'op-mode': 'ospf-ships-in-the-night', 'ospf-instance': {'af': 'address-family-ipv4', 'router-id': '101058049', 'ospf-area': {'area-id': '0', 'ospf-interface': {'name': 'GigabitEthernet2', 'network-type': 'ospf-broadcast', 'passive': 'false', 'demand-circuit': 'false', 'multi-area': {'multi-area-id': '0', 'cost': '0'}, 'node-flag': 'false', 'fast-reroute': {'candidate-disabled': 'false', 'enabled': 'false', 'remote-lfa-enabled': 'false'}, 'cost': '1', 'hello-interval': '10', 'dead-interval': '40', 'retransmit-interval': '5', 'transmit-delay': '1', 'mtu-ignore': 'false', 'lls': 'false', 'prefix-suppression': 'false', 'bfd': 'false', 'ttl-security': {'enabled': 'false', 'hops': '255'}, 'enable': 'true', 'authentication': {'no-auth': '1'}, 'state': 'BDR', 'hello-timer': '5', 'wait-timer': '40', 'dr': '8.8.8.1', 'bdr': '6.6.6.1', 'ospf-neighbor': {'neighbor-id': '8.8.8.1', 'address': '100.100.100.2', 'dr': '100.100.100.2', 'bdr': '100.100.100.1', 'state': 'ospf-nbr-exchange', 'stats': {'nbr-event-count': '4', 'nbr-retrans-qlen': '1'}}, 'priority': '0'}}, 'process-id': '1'}}, 'ospfv2-instance': {'instance-id': '1', 'vrf-name': None, 'router-id': '101058049', 'ospfv2-area': {'area-id': '0', 'ospfv2-lsdb-area': {'lsa-type': '1', 'lsa-id': '101058049', 'advertising-router': '101058049', 'lsa-age': '0', 'lsa-options': None, 'lsa-seq-number': '2147483749', 'lsa-checksum': '63365', 'lsa-length': '36', 'ospfv2-router-lsa-links': {'link-type': '3', 'link-id': '1684300800', 'link-data': '4294967292'}, 'router-lsa': {'router-lsa-bits': None, 'router-lsa-number-links': '1'}}, 'ospfv2-interface': {'name': 'GigabitEthernet2', 'network-type': 'ospf-broadcast', 'enable': 'true', 'passive': 'false', 'demand-circuit': 'false', 'mtu-ignore': 'false', 'prefix-suppresion': 'false', 'cost': '1', 'hello-interval': '10', 'dead-interval': '40', 'retransmit-interval': '5', 'transmit-delay': '1', 'hello-timer': '5378', 'wait-timer': '40000', 'dr': '134744065', 'bdr': '101058049', 'dr-ip': '100.100.100.2', 'bdr-ip': '100.100.100.1', 'state': 'ospfv2-interface-state-backup', 'ttl-security-val': {'enable': 'false', 'hops': '255'}, 'auth-val': {'no-auth': '1'}, 'ospfv2-neighbor': {'nbr-id': '134744065', 'address': '100.100.100.2', 'dr': '1684300802', 'bdr': '1684300801', 'dr-ip': '100.100.100.2', 'bdr-ip': '100.100.100.1', 'event-count': '4', 'retrans-count': '1', 'state': 'ospf-nbr-exchange', 'dead-timer': '35'}}}}}}

        print(var['ospf-oper-data']['ospf-state']['ospf-instance']['ospf-area']['ospf-interface']['ospf-neighbor']['state'])

def interface_statistics():
    var = {'interfaces-state': {'@xmlns': 'urn:ietf:params:xml:ns:yang:ietf-interfaces', 'interface': [{'name': 'GigabitEthernet1', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'admin-status': 'up', 'oper-status': 'up', 'last-change': '2025-02-24T19:15:48.000243+00:00', 'if-index': '1', 'phys-address': 'bc:24:11:e5:1a:b7', 'speed': '102400000', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000816+00:00', 'in-octets': '7845837', 'in-unicast-pkts': '66141', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '34555977', 'out-unicast-pkts': '69145', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'GigabitEthernet2', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'admin-status': 'up', 'oper-status': 'up', 'last-change': '2025-03-08T16:26:48.000924+00:00', 'if-index': '2', 'phys-address': 'bc:24:11:17:f0:19', 'speed': '1024000000', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000815+00:00', 'in-octets': '110049726', 'in-unicast-pkts': '1796236', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '185970009', 'out-unicast-pkts': '2551942', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'GigabitEthernet3', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'admin-status': 'down', 'oper-status': 'down', 'last-change': '2025-02-24T19:15:56.000112+00:00', 'if-index': '3', 'phys-address': 'bc:24:11:75:e4:10', 'speed': '1024000000', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000814+00:00', 'in-octets': '73403', 'in-unicast-pkts': '523', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '0', 'out-unicast-pkts': '0', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'GigabitEthernet4', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'admin-status': 'down', 'oper-status': 'down', 'last-change': '2025-02-24T19:15:56.000115+00:00', 'if-index': '4', 'phys-address': 'bc:24:11:0b:0c:3f', 'speed': '1024000000', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000814+00:00', 'in-octets': '73403', 'in-unicast-pkts': '523', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '0', 'out-unicast-pkts': '0', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'GigabitEthernet5', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:ethernetCsmacd'}, 'admin-status': 'down', 'oper-status': 'down', 'last-change': '2025-02-24T19:15:56.000077+00:00', 'if-index': '5', 'phys-address': 'bc:24:11:a2:4d:83', 'speed': '1024000000', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000813+00:00', 'in-octets': '73403', 'in-unicast-pkts': '523', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '0', 'out-unicast-pkts': '0', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'Loopback0', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:softwareLoopback'}, 'admin-status': 'up', 'oper-status': 'up', 'last-change': '2025-02-27T18:16:08.000772+00:00', 'if-index': '8', 'phys-address': '00:1e:14:59:9b:00', 'speed': '3897032704', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000813+00:00', 'in-octets': '0', 'in-unicast-pkts': '0', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '0', 'out-unicast-pkts': '0', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'Loopback1', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:softwareLoopback'}, 'admin-status': 'up', 'oper-status': 'up', 'last-change': '2025-02-27T18:16:54.000737+00:00', 'if-index': '12', 'phys-address': '00:1e:14:59:9b:00', 'speed': '3897032704', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000812+00:00', 'in-octets': '0', 'in-unicast-pkts': '0', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '0', 'out-unicast-pkts': '0', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}, {'name': 'Control Plane', 'type': {'@xmlns:ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type', '#text': 'ianaift:other'}, 'admin-status': 'up', 'oper-status': 'up', 'last-change': '2025-02-24T19:15:11.000329+00:00', 'if-index': '0', 'phys-address': '00:00:00:00:00:00', 'speed': '1650065408', 'statistics': {'discontinuity-time': '2025-02-24T19:07:46.000811+00:00', 'in-octets': '0', 'in-unicast-pkts': '0', 'in-broadcast-pkts': '0', 'in-multicast-pkts': '0', 'in-discards': '0', 'in-errors': '0', 'in-unknown-protos': '0', 'out-octets': '0', 'out-unicast-pkts': '0', 'out-broadcast-pkts': '0', 'out-multicast-pkts': '0', 'out-discards': '0', 'out-errors': '0'}}]}}
    print(json.dumps(var,indent=4))


def main():
    # telegraf_line_protocol = influxdb_format()
    # influxdb_write(telegraf_line_protocol)
    # # influx_client()
    # influx_client()
    # entry()
    # compat()
    interface_statistics()




main()