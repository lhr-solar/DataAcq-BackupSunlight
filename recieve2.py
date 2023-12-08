import os
import can

os.system('sudo ip link set can0 type can bitrate 125000')
os.system('sudo ifconfig can0 up')

can0 = can.Bus(channel = 'can0', interface = 'socketcan')# socketcan_native

print("RUNNING")
msg = can0.recv(2)

if msg:
    print(msg)
else:
    print("No message received")

os.system('sudo ifconfig can0 down')