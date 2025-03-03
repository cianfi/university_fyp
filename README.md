# university_fyp
This is the Final Year Project for my University Degree. 

# Telegraf 
The telegraf service within docker-compose file calls the dockerfile within "./telegraf/". 

The dockerfile does:
1) Calls the latest telegraf image.
2) Copys over "./telegraf/configuration/" and moves it to "/tmp/configuration/" within the container. 
3) Moves the different ".conf" files to its relative path, the ".py" file and devices directory to its relative path. For example:
    - telegraf.conf --> /etc/telegraf/telegraf.conf
    - stream_telem.conf --> /etc/telegraf/telegraf.d/stream_telem.conf
    - netconf.conf --> /etc/telegraf/telegraf.d/netconf.conf
    - devices/ --> /etc/telegraf/
    - ncclient_telegraf.py --> /etc/telegraf/
4) Install the neccessary packages and configure the python virtual environment.
5) Set arguements.

The telegraf set up for this project will open ports 57500 and 8080. Port 57500 is open to allow us to configure streaming telemetry if the router OS supports it. Port 8080 is open so we can do testing incase of any issues. 

In this scenario, the Cisco IOS versions I am using do not support streaming telemetry, so instead I have created a configuration file called "netconf.conf". This performs a "pulling telemetry" method. The "netconf.conf" file runs the python script to collect the neccessary NETCONF data from our devices and send it to InfluxDB for storage. 