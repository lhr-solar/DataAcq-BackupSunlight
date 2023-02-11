import os
import can

# os.system('sudo ip link set can0 type can bitrate 125000')
# os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native

msg = can.Message(arbitration_id=0x1, data=[0, 1])
print(msg.data)
can0.send(msg)
# os.system('sudo ifconfig can0 down')