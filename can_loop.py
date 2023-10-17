import socket
import logging
import queue as Queue

import asyncio
import os
from typing import List

import can
from can.notifier import MessageRecipient

from eth_socket import ClientDisconnectError, reconnect_socket


HOST = '169.254.173.129'
PORT = 65432

# os.system('sudo ifconfig can0 down')
# os.system('sudo ip link set can0 type can bitrate 125000')
# os.system('sudo ifconfig can0 up')

queue = Queue.SimpleQueue()

def can_msg_cb(msg: can.Message) -> None:
    """Regular callback function. Can also be a coroutine."""
    # for _ in range(80):
    #     list(map(lambda msg: queue.put(msg), CAN_Test_Data))
    queue.put(msg, False)

async def can_loop() -> None:
    """The main function that runs in the loop."""
    logging.info("CAN Loop Started")

    with can.Bus(
        interface="virtual", channel="vcan0", receive_own_messages=True
    ) as bus:
        reader = can.AsyncBufferedReader()
        logger = can.Logger("logfile.asc")

        listeners: List[MessageRecipient] = [
            can_msg_cb,  # Callback function
            reader,  # AsyncBufferedReader() listener
            logger,  # Regular Listener object
        ]
        # Create Notifier with an explicit loop to use for scheduling of callbacks
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(bus, listeners, loop=loop)

        while notifier._running:
            await asyncio.sleep(0)

queue_empty_delay = 0.03
async def send_can(s: socket.socket):
    while True:
        try:
            while (i := queue.get(False)):
                try:
                    buf = bytearray(i)
                    s.send(buf)
                    logging.debug("Sent Buffer")

                except ClientDisconnectError:
                    s = reconnect_socket()
        except Queue.Empty as e:
            await asyncio.sleep(queue_empty_delay) 
        await asyncio.sleep(0)
        
if __name__ == "__main__":
    asyncio.run(can_loop())
