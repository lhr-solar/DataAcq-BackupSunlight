import can, os

os.system('sudo ip link set can0 type can bitrate 125000')
os.system('sudo ifconfig can0 up')

with can.Bus(channel = 'can0', interface = 'socketcan') as bus:
    while True:
        msg = bus.recv()
        # canBuffer = bytearray()
        

        print(msg)