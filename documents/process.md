# Process
...

## Network Devices
The network topology for this project consists of two Cisco CSR1000v both running a firmware version of 16.09.07. These two routers were configured and hosted on a Proxmox server. The two network devices were configured with Netconf-yang, which allowed us to use python scripts to grab the data, which is the purpose of the Data Collector.

## Data Collector
...

## InfluxDB
...

## Grafana
The Grafana instance for this project currently contains two dashboards:
    - Router 1 - OSPF
    - Router 1 - BGP

The two dashboards contain three visualisations currently, however this will be brought to two. 

For OSPF dashboard we have:
    - OSPF State
    - Interface Status

For BGP dashboard we have:
    - BGP State
    - Interface Status

There is a 'contact point' configured for a webhook. When used, it will create a 'POST' request to the API server 'http://host.docker.internal:8000/alert' which will then carry on the rest of the process seen in the file 'process.drawio'.

There is a 'notification policy' configured. The configurations look like this:
    - '0 seconds' when alert is triggered to send a notification to the 'contact point'. 
    - '10 seconds' when the alert is resolved to send a notification to the 'contact point'.
    - '4 hours' when the alert is still triggered to send another notification to the 'contact point'. 
    - NOTE: 4 hours so we dont cause loops within the LLM process. 

There is two 'alert rules' currently configured. They are:
    - BGP State 
    - OSPF State
    - Both of these are configured to trigger when the dashboard goes below '1'. For the two status pages, it is configured to present "'up status' == 1" and "'down status' == 0". Every '10 seconds' the visualisations are being evaluated and triggered in '0s' if they drop below 0, which starts the alerting process. 

## Alert API


## AI Agent