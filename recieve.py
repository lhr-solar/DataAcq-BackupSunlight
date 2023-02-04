import os
import can
import listener

os.system('sudo ip link set can0 type can bitrate 100000')
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native
can_listener = listener.Listener()

#msg = can.Message(arbitration_id=0x123, data=[0, 1, 2, 3, 4, 5, 6, 7], is_extended_id=False)
i = 0

while(i < 10):
    msg = can0.recv()
    can_listener.on_message_received(msg)

can_listener.stop()

os.system('sudo ifconfig can0 down')
