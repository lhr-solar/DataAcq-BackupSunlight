#!/bin/bash

sudo ifconfig can0 down
sudo ifconfig can1 down
sudo ip link set can0 type can bitrate 125000
sudo ip link set can1 type can bitrate 125000
sudo ifconfig can0 txqueuelen 65536
sudo ifconfig can1 txqueuelen 65536
sudo ifconfig can0 up
sudo ifconfig can1 up

# Will need to add execution permission to file
# chmod +x myscript.sh
# Need to add to PI's start up files 
# ./myscript.sh
