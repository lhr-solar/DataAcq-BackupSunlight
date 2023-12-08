import socket
import logging
import multiprocessing
import time

import queue as Queue

import asyncio
import os
from typing import List

import can
from can.notifier import MessageRecipient

from sim.main import CAN_Test_Data


HOST = '169.254.146.29'
PORT = 65432

os.system('sudo ifconfig can0 down')
os.system('sudo ip link set can0 type can bitrate 125000')
os.system('sudo ifconfig can0 up')

# queue = Queue.SimpleQueue()


def print_message(msg: can.Message, queue: multiprocessing.Queue) -> None:
    """Regular callback function. Can also be a coroutine."""
    # print(msg)
    # for _ in range(80):
    #     list(map(lambda msg: queue.put(msg), CAN_Test_Data))
    queue.put(bytearray(msg.data), False)


async def canLoop(queue: multiprocessing.Queue) -> None:
    """The main function that runs in the loop."""

    with can.Bus(  # type: ignore
        interface="socketcan", channel="can0", receive_own_messages=False
    ) as bus:
        reader = can.AsyncBufferedReader()
        logger = can.Logger("logfile.asc")

        listeners: List[MessageRecipient] = [
            # (print_message, (queue, )),  # Callback function
            # # Queue #I dont know how to put queue into parameter of call back function
            reader,  # AsyncBufferedReader() listener
            logger,  # Regular Listener object
        ]
        # # Create Notifier with an explicit loop to use for scheduling of callbacks
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(bus, listeners, loop=loop)
        # Start sending first message

        # print("Sending CAN messages...")

        # asyncio.ensure_future(sender(s))

        # bus.send(can.Message(arbitration_id=0))
        while True:
            # print("a")
            # msg = reader.get_message()
            # print(msg)
            msg = await reader.get_message()
            print(msg)
            if (msg is not None):
                print(msg)
                print_message(msg, queue)
                print("Sent CAN Message")
            # queue.put(msg, False)
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


def sender(s, queue: multiprocessing.Queue):

    while True:
        try:
            while (i := queue.get()):
                try:
                    print(f'Queue Size: {queue.qsize()}')
                    buf = bytearray(i)
                    s.send(buf)

                except ClientDisconnectError:
                    print("Client Disconnect Error")
                    s = reconnect_socket(s)
        except Queue.Empty as e:
            pass


# async def main(queue):
#    asyncio.ensure_future(canLoop(queue))

def run(queue):
    asyncio.run(canLoop(queue))
# Use multiprocessing or multithreading


if __name__ == "__main__":
    # logging.basicConfig(level=logging.WARNING)
    # asyncio.ensure_future(canLoop())
    # sender()
    logging.warning("Client starting...")
    s = socket.create_connection(address=(HOST, PORT))
    queue = multiprocessing.Manager().Queue()

    pool = multiprocessing.Pool(processes=2)
    
    results = [pool.apply_async(run, (queue,)), pool.apply_async(sender, (s, queue,)) ]
    for result in results:
        result.get()
    
    # p = multiprocessing.Process(target=sender, args=(queue,))
    # p.start()
    # p2 = multiprocessing.Process(target=canLoop, args=(queue,))
    # p2.start()
    
    # processes = [p, p2]
    
    # for process in processes:
    #     process.join()
