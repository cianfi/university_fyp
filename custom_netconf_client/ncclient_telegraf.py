from typing import Dict
from ncclient import manager
import xmltodict
import json
import dataclasses
import argparse
import logging

@dataclasses.dataclass
class DeviceData:
    name: str
    ip_address: str
    port: int
    username: str
    password: str
    os: str

@dataclasses.dataclass
class ReplyData:
    device_name: str
    reply: dict


def device_details(device_file_path: str) -> DeviceData:
    with open(device_file_path, "r") as raw_device:
        device = json.load(raw_device)
        return DeviceData(
            name=device["name"],
            ip_address=device["ip_address"],
            port=device["port"],
            username=device["username"],
            password=device["password"],
            os=device["os"],
        )


def arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=str, required=True)
    parser.add_argument("--filter", type=str, required=True)
    args = parser.parse_args()

    if ".json" not in args.device:
        raise ValueError("Must be a '.json' file")
    else:
        device: DeviceData = device_details(device_file_path=args.device)

    netconf_filter_dict: dict = {
        "interface_status": NetconfFilter.interface_status(),
        "interface_statistics": NetconfFilter.interface_statistics(),
        "bgp_status": NetconfFilter.bgp_status(),
        "hsrp_status": NetconfFilter.hsrp_status(),
    }

    if args.filter in netconf_filter_dict:
        netconf_filter = netconf_filter_dict.get(args.filter)
    else:
        raise ValueError("Incorrect Filter")
    
    return device, netconf_filter


def connecter(netconf_filter: str,  device: DeviceData) -> ReplyData:
    with manager.connect(
        host = device.ip_address,
        port = device.port,
        username = device.username,
        password = device.password,
        hostkey_verify=False, 
    ) as connect:
        
        netconf_rpc_reply = connect.get(filter = netconf_filter).xml
        # .xml returns a string type.
        # nothing returns a ncclient type. 

    xml_to_dict = xmltodict.parse(netconf_rpc_reply)

    # This will check to see if nothing is returned. If nothing returned, issue with filter which will be flagged. 
    if xml_to_dict["rpc-reply"]["data"] == None:
        logging.error(f"NO DATA RETURNED. NETCONF FILTER: {netconf_filter}")
        return ReplyData(
            device_name=device.name,
            reply=f"No data was returned via this filter: {netconf_filter}"
        )
    else:
        logging.info("DATA RETURNED. SENDING TO TELEGRAF")
        return ReplyData(
            device_name=device.name,
            reply=xml_to_dict["rpc-reply"]["data"],
        )


def telegraf_format(device_reply: ReplyData):
    return json.dumps(
        {
            "device_name": device_reply.device_name,
            "data": device_reply.reply
        })
    

class NetconfFilter():
    @staticmethod
    def interface_status() -> str:
        """This is a function that returns the netconf filter needed to collect the interfaces status"""
        return """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                            <interface>
                                <name/>
                                <admin-status/>
                                <oper-status/>
                            </interface>
                        </interfaces-state>
                    </filter>"""

    @staticmethod
    def interface_statistics() -> str:
        """This is a function that returns the netconf filter needed to collect the interfaces statistics """
        return """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces/interface/statistics">
                        </interfaces-state>
                    </filter>"""

    @staticmethod
    def bgp_status() -> str:
        """This is a function that returns the netconf filter needed to collect bgp neighbor status """
        return """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <bgp-state-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-bgp-oper">
                            <neighbors/>
                        </bgp-state-data>
                    </filter> """

    @staticmethod
    def hsrp_status() -> str:
        """This is a function that returns the netconf filter needed to collect hsrp status """
        return """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <vrrp-state-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vrrp-oper">
                        </vrrp-state-data>
                    </filter>"""


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("telegraf_netconf.log"),
            # logging.StreamHandler() 
        ]
    )

    args = arg_parser()
    device_agent = connecter(device=args[0], netconf_filter=args[1])
    test = telegraf_format(device_reply=device_agent)
    print(test)


if __name__ == "__main__":
    main()