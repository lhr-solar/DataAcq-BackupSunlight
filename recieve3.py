import can, os

os.system('sudo ip link set can0 type can bitrate 125000')
os.system('sudo ifconfig can0 up')

def receive_can_messages(bus):
    while True:
        messages = bus.get_message()
        while messages is not None:
            print(f"Received message: {messages}")
            messages = bus.get_message()

bus = can.BufferedReader(can.Bus(bustype='socketcan', channel='can0'))
receive_can_messages(bus)