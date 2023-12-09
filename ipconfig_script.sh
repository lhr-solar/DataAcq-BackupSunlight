#!/bin/bash

# Check if the script is run with sudo
if [ "$EUID" -ne 0 ]; then
    echo "ipconfig script requires superuser privileges. Please run with sudo - script terminated"
    exit 1
fi

# Run the actual script 
ifconfig can0 down
ifconfig can1 down
ip link set can0 type can bitrate 125000
ip link set can1 type can bitrate 125000
ifconfig can0 txqueuelen 65536
ifconfig can1 txqueuelen 65536
ifconfig can0 up
ifconfig can1 up

# Will need to add execution permission to file
# chmod +x ipconfig_script.sh
# Need to add to Pi's start up files (local.rc?)
# ./ipconfig_script.sh
