import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.simplefilter(action="ignore", category=CryptographyDeprecationWarning)

from ncclient import manager
import xmltodict
import json
import dataclasses
import argparse
import logging
import threading
import requests
import os
from models import DeviceData, ReplyData, TelegrafFormat


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
    """Returns five variables:
        args.env
        arg.url
        device
        args.filter
        netconf_filter    
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--env", type=str, required=True)
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--device", type=str, required=True)
    parser.add_argument("--filter", type=str, required=False)
    
    args = parser.parse_args()
    if ".json" not in args.device:
        raise ValueError("Must be a '.json' file")
    else:
        device: DeviceData = device_details(device_file_path=args.device)

    if args.env == "local":
        netconf_filter_dict: dict = {
            "interface_status": NetconfFilter.interface_status(),
            "interface_statistics": NetconfFilter.interface_statistics(),
            "bgp_status": NetconfFilter.bgp_status(),
            "ospf_status": NetconfFilter.ospf_status(),
        }
        if args.filter in netconf_filter_dict:
            netconf_filter = netconf_filter_dict.get(args.filter)
        else:
            raise ValueError("Incorrect Filter")

        return args.env, args.url, device , args.filter, netconf_filter

    elif args.env == "container":
        args.filter = None
        netconf_filter = None
    
        return args.env, args.url, device, args.filter, netconf_filter


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
        return ReplyData(
            device_name=device.name,
            reply=None
        )
    else:
        return ReplyData(
            device_name=device.name,
            reply=xml_to_dict["rpc-reply"]["data"],
        )


class InfluxDBFormatter():
    def __init__(self, url: str):
        self.url = url
        self.Influx = InfluxDBConnect(url=url)

    def interface_status(self, device_data: ReplyData):
        for data in device_data.reply:
        
            telegraf_dict: list[dict] = []

            for individual_interface in device_data.reply[data]["interface"]:
                    telegraf_dict.append({
                        "measurement": "interface_status",
                        "tags": {
                            "device_name": device_data.device_name,
                            "interface_name": individual_interface["name"],
                        },
                        "fields": {
                            "admin_status": individual_interface["admin-status"],
                            "oper_status": individual_interface["oper-status"]
                        },
                    })

        influxdb_line_protocol: list[str] = self._line_protocol(telegraf_dict)

        for entry in influxdb_line_protocol:
            if "Control Plane" in entry:
                influxdb_line_protocol.remove(entry)

        response = self.Influx.request_write(influxdb_line_protocol)
        return response

    def interface_statistics(self, device_data: ReplyData):
        pass

    def bgp_status(self, device_data: ReplyData):
        telegraf_dict: list[dict] = []
    
        for key,value in device_data.reply["bgp-state-data"]["neighbors"].items():
            telegraf_dict.append(
                {
                    "measurement": "bgp_status",
                    "tags": {
                        "device_name": device_data.device_name,
                        "neighbor_id": value["neighbor-id"],
                    },
                    "fields": {
                        "bgp_state": value["connection"]["state"],
                    }
                }
            )
        influxdb_line_protocol: list[str] = self._line_protocol(telegraf_dict)
        response = self.Influx.request_write(influxdb_line_protocol)
        return response

    def ospf_status(self, device_data: ReplyData):
        ospf_state_types: list[str] = ["BDR", "DR", "Down"]
        telegraf_list: list[dict] = []

        short = device_data.reply["ospf-oper-data"]["ospf-state"]["ospf-instance"]["ospf-area"]["ospf-interface"]

        if type(short) is list:
            for interface in short:
                if interface["state"] in ospf_state_types:
                    telegraf_list.append(self._ospf_short(device_data.device_name, interface))
                else:
                    pass

        elif type(short) is dict:
            telegraf_list.append(self._ospf_short(device_data.device_name, interface))

        else:
            raise ValueError("Please check OSPF")

        influxdb_line_protocol: list[str] = self._line_protocol(telegraf_list)
        response = self.Influx.request_write(influxdb_line_protocol)
        return response

    def _ospf_short(self, device_name, interface):
            if 'ospf-neighbor' in interface:
                return {
                        "measurement": "ospf_status",
                        "tags": {
                            "device_name": device_name,
                        },
                        "fields": {
                            "ospf_state": interface["ospf-neighbor"]["state"]
                        }
                    }
                
            elif 'state' in interface:
                if interface['state'] == "Down":
                    return {
                            "measurement": "ospf_status",
                            "tags": {
                                "device_name": device_name,
                            },
                            "fields": {
                                "ospf_state": "Down"
                            }
                        }
                    

    def _line_protocol(self, telegraf_dict) -> list[str]:
        influxdb_line_protocol: list[str] = []
        
        for mtf in telegraf_dict:
            line_protocol_tags = ",".join(f'{k}={v}' for k,v in mtf["tags"].items())
            line_protocol_fields = ",".join(f'{k}="{v}"' for k,v in mtf["fields"].items())

            line_protocol_entry = f"{mtf['measurement']}"
            line_protocol_entry += f",{line_protocol_tags}"
            line_protocol_entry += f" {line_protocol_fields}"
            influxdb_line_protocol.append(line_protocol_entry)

        return influxdb_line_protocol


class InfluxDBConnect():
    def __init__(self, url):
        self.url = url

    def request_write(self, influxdb_line_protocol):
        payload = ""
        counter = 0
        while counter < len(influxdb_line_protocol):
            if counter != 0:
                payload += f"\n{influxdb_line_protocol[counter]}"
            else:
                payload += f"{influxdb_line_protocol[counter]}"
            counter += 1

        response = requests.request(
            method="POST",
            url=f"http://{self.url}:8086/api/v2/write",
            headers={
                "Accept": "application/json",
                "Content-Type": "text/plain",
                "Authorization": f"Token {os.environ.get('INFLUXDB_TOKEN')}",
                },
            params={
                "bucket": "network-data",
                "org": "my-org"
                },
            data=payload,
            verify=False,
        )
        return response


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
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
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
    def ospf_status() -> str:
        """This is a function that returns the netconf filter needed to collect hsrp status """
        return """
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <ospf-oper-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf-oper">
                </ospf-oper-data>
            </filter>
                """


class ScriptType():
    def __init__(self, url, device, filter, netconf_filter):
        self.url = url
        self.device = device
        self.filter = filter
        self.netconf_filter = netconf_filter

    def container(self):
        # Container will run all scenarios of data. Interface status, stats, bgp status and hsrp status
        Influx = InfluxDBFormatter(url=self.url)

        netconf_dict: dict = {
            "interface_status": {
                "filter": NetconfFilter.interface_status(),
                "formatter": Influx.interface_status,
            },
            # "interface_statistics": {
            #     "filter": NetconfFilter.interface_statistics(),
            #     "formatter": Influx.interface_statistics,
            # },
            "bgp_status": {
                "filter": NetconfFilter.bgp_status(),
                "formatter": Influx.bgp_status,
            },
            "ospf_status": {
                "filter": NetconfFilter.ospf_status(),
                "formatter": Influx.ospf_status
            }
        }

        for entry in netconf_dict:
            device_agent = connecter(
                device=self.device,
                netconf_filter=netconf_dict[entry]["filter"],
                )
            if device_agent.reply != None:
                response = netconf_dict[entry]["formatter"](device_agent)
                self._response(response, entry)
            else:
                logging.info(f"No data retrieved for '{entry}'")
                continue

    def local(self):
        device_data: ReplyData = connecter(device=self.device, netconf_filter=self.netconf_filter)
        Influx = InfluxDBFormatter(url=self.url)

        if device_data.reply == None:
            logging.info(f"Unsuccessful Response: No data for '{self.filter}'")
            quit()

        if self.filter == "interface_status":
            Influx.interface_status(device_data)
        elif self.filter == "interface_statistics":
            Influx.interface_statistics(device_data)
        elif self.filter == "bgp_status":
            Influx.bgp_status(device_data)
        elif self.filter == "ospf_status":
            Influx.ospf_status(device_data)

    def _response(self, response, entry: str):
        if response.status_code < 200 or response.status_code >= 300:
            logging.info(f"Unsuccessful response: {response.status_code}. Message {response.text}")
        else:
            logging.info(f"Successful Response for '{entry}': {response.status_code}")


def main():
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("datacollecter.log"),
        ]
        )

    logging.getLogger("ncclient").setLevel(logging.WARNING)
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.info("Starting Script")

    args = arg_parser()
    script = ScriptType(
        url=args[1],
        device=args[2],
        filter=args[3],
        netconf_filter=args[4],
        )

    if args[0] == "container":
        script.container()
        logging.info(f"Done script. Waiting 30 seconds.")
    elif args[0] == "local":
        script.local()
        logging.info(f"Done '{args[3]}'. Waiting 30 seconds.")

    
    threading.Timer(30, main).start()

if __name__ == "__main__":
    main()