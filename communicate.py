import socket
import logging
import time

import asyncio
import os
from typing import List

import can
from can.notifier import MessageRecipient

from sim.main import CAN_Test_Data


HOST = '169.254.240.155'
PORT = 65432

os.system('sudo ip link set can0 type can bitrate 125000')
os.system('sudo ifconfig can0 up')

queue = []

def print_message(msg: can.Message) -> None:
    """Regular callback function. Can also be a coroutine."""
    print(msg)
    global queue
    queue += [msg] #comment

async def canLoop() -> None:
    """The main function that runs in the loop."""
    logging.warning("Client starting...")
    s = socket.create_connection(address=(HOST, PORT))
    
    with can.Bus(  # type: ignore
        interface="socketcan", channel="can0", receive_own_messages=False
    ) as bus:
        reader = can.AsyncBufferedReader()
        logger = can.Logger("logfile.asc")

        listeners: List[MessageRecipient] = [
            print_message,  # Callback function
            reader,  # AsyncBufferedReader() listener
            logger,  # Regular Listener object
        ]
        # Create Notifier with an explicit loop to use for scheduling of callbacks
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(bus, listeners, loop=loop)
        # Start sending first message
        # bus.send(can.Message(arbitration_id=0))

        print("Sending CAN messages...")
                
        asyncio.ensure_future(sender(s))
        
        while True:
            # print("a")
            await reader.get_message()
            # sender()
            # print("b")
            # await asyncio.sleep(0.5)
            # msg.arbitration_id += 1
            # bus.send(msg)
        # os.system('sudo ifconfig can0 down')
        # Clean-up
        # notifier.stop()


def reconnect_socket(client: socket) -> socket:

    logging.warning("Client disconnect")
    client.close()
    logging.warning("Client reconnecting...")
    return socket.create_connection(address=(HOST, PORT))


class ClientDisconnectError(Exception):
    pass

async def sender(s):
    print("sender")
    i = 0
    while True:
        await asyncio.sleep(0)
        while len(queue) > 0:
            print("LEN: ", len(queue))
            try:
                buf = bytearray(queue.pop(0))
                s.send(buf)

            except ClientDisconnectError:
                s = reconnect_socket(s)
            await asyncio.sleep(0)
                
# async def main():
#     asyncio.ensure_future(canLoop())
    
    

if __name__ == "__main__":
    # logging.basicConfig(level=logging.WARNING)
    # asyncio.ensure_future(canLoop())
    # sender()
    asyncio.run(canLoop())
