import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.simplefilter(action="ignore", category=CryptographyDeprecationWarning)

from ncclient import manager
import xmltodict
import json
import argparse
import logging
import threading
import requests
import os
from models import DeviceData, ReplyData, ScriptArgs


def device_details(device_file_path: str) -> DeviceData:
    """
    This function will read the './network/testbed.yaml' file and return a DeviceData
    object which contains the device name, ip address, port, username, password and os of the device.

    Args:
        device_file_path (str): The path to the device file.

    Returns:
        DeviceData: A DeviceData object containing the device details.
    """
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

def arg_parser() -> ScriptArgs:
    """
    This function will parse the command line arguments and return the environment, url, device, filter and netconf_filter.

    Args:
        None

    Returns:
        tuple: A tuple containing the environment, url, device, filter and netconf_filter.  
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

    # Check if the device is a container or local. Local is easier for testing, container will run as a continious loop.
    if args.env == "local":
        netconf_filter_dict: dict = {
            "interface_status": NetconfFilter.get_filter("interface_status"),
            "interface_statistics": NetconfFilter.get_filter("interface_statistics"),
            "bgp_status": NetconfFilter.get_filter("bgp_status"),
            "ospf_status": NetconfFilter.get_filter("ospf_status"),
        }
        if args.filter in netconf_filter_dict:
            netconf_filter = netconf_filter_dict.get(args.filter)
        else:
            raise ValueError("Incorrect Filter")

        return ScriptArgs(env=args.env, url=args.url, device=device, filter=args.filter, netconf_filter=netconf_filter)

    elif args.env == "container":
        args.filter = None
        netconf_filter = None
    
        return ScriptArgs(env=args.env, url=args.url, device=device, filter=args.filter, netconf_filter=netconf_filter)

def connecter(netconf_filter: str,  device: DeviceData) -> ReplyData:
    """
    This function will connect to the device using netconf and return the data.
    It will use the netconf filter to get the data from the device.

    Args:
        netconf_filter (str): The netconf filter to use.
        device (DeviceData): The device to connect to.

    Returns:
        ReplyData: A ReplyData object containing the device name and the reply data.
    """
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

    def interface_status(self, device_data: ReplyData) -> requests.Response:
        """
        This function will format the interface status data to line protocol and send it to InfluxDB.

        Args:
            device_data (ReplyData): The device data to format.

        Returns:
            None
        """
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

    def bgp_status(self, device_data: ReplyData) -> requests.Response:
        """
        This function will format the BGP status data to line protocol and send it to InfluxDB.

        Args:
            device_data (ReplyData): The device data to format.

        Returns:  
            None
        """
        telegraf_list: list[dict] = []
    
        for key,value in device_data.reply["bgp-state-data"]["neighbors"].items():
            telegraf_list.append(
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
        return self._format_and_send(telegraf_list)

    def ospf_status(self, device_data: ReplyData) -> requests.Response:
        """
        This function will format the OSPF status data to line protocol and send it to InfluxDB.

        Args:
            device_data (ReplyData): The device data to format.

        Returns:
            None
        """
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

        return self._format_and_send(telegraf_list)

    def _format_and_send(self, telegraf_dict: list[dict]) -> requests.Response:
        """
        This function will format the telegraf data to line protocol and send it to InfluxDB.

        Args:
            telegraf_dict (list[dict]): The telegraf data to format.

        Returns:
            None
        """
        influxdb_line_protocol: list[str] = self._line_protocol(telegraf_dict)
        response = self.Influx.request_write(influxdb_line_protocol)
        return response

    def _ospf_short(self, device_name: str, interface: dict) -> dict:
        """
        This function is called within the OSPF function to format the OSPF data to line protocol.
        It will check if the interface is a list or a dict and format the data accordingly.

        Args:
            device_name (str): The device name.
            interface (dict): The interface data.
        """
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
                    
    def _line_protocol(self, telegraf_dict: list[dict]) -> list[str]:
        """
        This function will format the telegraf data to line protocol.
        It will loop through the telegraf_dict and format the data to line protocol.
        It will return a list of line protocol entries.

        Args:
            telegraf_dict (list[dict]): The telegraf data to format.

        Returns:
            list[str]: A list of line protocol entries.
        """
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

    def request_write(self, influxdb_line_protocol: list[str]) -> requests.Response:   
        """
        This function will send the data to InfluxDB via requests library.
        It will take the influxdb_line_protocol and send it to InfluxDB API.

        Args:
            influxdb_line_protocol (list[str]): The influxdb line protocol data to send.

        Returns:
            response: The response from InfluxDB API.
        """
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
    Filters = {
        "interface_status": """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                            <interface>
                                <name/>
                                <admin-status/>
                                <oper-status/>
                            </interface>
                        </interfaces-state>
                    </filter>""",
        "interface_statistics": """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                        </interfaces-state>
                    </filter>""",
        "bgp_status": """<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <bgp-state-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-bgp-oper">
                            <neighbors/>
                        </bgp-state-data>
                    </filter> """,
        "ospf_status": """
            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <ospf-oper-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf-oper">
                </ospf-oper-data>
            </filter>
                """,}

    @staticmethod
    def get_filter(filter_name: str) -> str:
        """
        This function will return the filter based on the filter name.

        Args:
            filter_name (str): The name of the filter.

        Returns:
            str: The filter.
        """
        if filter_name in NetconfFilter.Filters:
            return NetconfFilter.Filters.get(filter_name)
        else:
            raise ValueError("Incorrect Filter")

class ScriptType():
    def __init__(self, url, device, filter, netconf_filter):
        self.url = url
        self.device = device
        self.filter = filter
        self.netconf_filter = netconf_filter

    def container(self):
        """
        This function will be called if arg --env is set to 'container'.
        It will run all the filters and send the data to InfluxDB.

        Args:
            None

        Returns:
            None
        """
        # Set up the InfluxDB connection by creating an instance of the InfluxDBFormatter class.
        Influx = InfluxDBFormatter(url=self.url)

        # Set up the netconf filters and formatters in a dictionary.
        netconf_dict: dict = {
            "interface_status": {
                "filter": NetconfFilter.get_filter("interface_status"),
                "formatter": Influx.interface_status,
            },
            "bgp_status": {
                "filter": NetconfFilter.get_filter("bgp_status"),
                "formatter": Influx.bgp_status,
            },
            "ospf_status": {
                "filter": NetconfFilter.get_filter("ospf_status"),
                "formatter": Influx.ospf_status
            }
        }

        # Loop through the netconf_dict and connect to the device using the different netconf filter.
        for entry in netconf_dict:

            # Connect to the device using the netconf filter and get the data.
            device_agent = connecter(
                device=self.device,
                netconf_filter=netconf_dict[entry]["filter"],
                )
            
            # Check if the device_agent reply is None. If it is, log the message and continue to the next entry.
            # There was an issue with the filter for OSPF, so had to make a speicific check for it.
            if (entry == "ospf_status" and
                "ospf-instance" not in device_agent.reply["ospf-oper-data"]["ospf-state"]):
                logging.info(f"No data retrieved for 'ospf_status'")
                continue

            # If the device_agent reply is not None, format the data and send it to InfluxDB.
            if device_agent.reply != None:
                response = netconf_dict[entry]["formatter"](device_agent)
                self._response(response, entry)
            else:
                logging.info(f"No data retrieved for '{entry}'")
                continue

    def local(self):
        """
        This function will be called if arg --env is set to 'local'.
        It will run the specific filter thats called and send the data to InfluxDB.

        Args:
            None

        Returns:
            None
        """
        device_data: ReplyData = connecter(device=self.device, netconf_filter=self.netconf_filter)
        Influx = InfluxDBFormatter(url=self.url)


        if device_data.reply == None:
            logging.info(f"Unsuccessful Response: No data for '{self.filter}'")
            return
        elif (
            self.filter == "ospf_status" and 
            "ospf-instance" not in device_data.reply["ospf-oper-data"]["ospf-state"]):
                logging.error("Unsuccessful Response: No data for 'ospf_status'")
                return
        else:
            pass

        if self.filter == "interface_status":
            Influx.interface_status(device_data)
        elif self.filter == "bgp_status":
            Influx.bgp_status(device_data)
        elif self.filter == "ospf_status":
            Influx.ospf_status(device_data)

    def _response(self, response, entry: str):
        if response.status_code < 200 or response.status_code >= 300:
            logging.error(f"Unsuccessful response: {response.status_code}. Message {response.text}")
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

    # Parse the command line arguments.
    args = arg_parser()

    # Create a ScriptType object with the parsed arguments.
    script = ScriptType(
        url=args.url,
        device=args.device,
        filter=args.filter,
        netconf_filter=args.netconf_filter,
        )

    # Check if the script is running in a container or locally.
    # If running in a container, run all the filters. If running locally, run the filter specified in the command line.
    if args.env == "container":
        script.container()
        logging.info(f"Done script. Waiting 10 seconds.")
    elif args.env == "local":
        script.local()
        logging.info(f"Done '{args.filter}'. Waiting 10 seconds.")

    # Forces the script to run every 10 seconds after it has finished.
    threading.Timer(10, main).start()

if __name__ == "__main__":
    main()