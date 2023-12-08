from ctypes import Array
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

CANIDs = {
    0x001: 0,
    0x002: 0,
    0x003: 0,
    0x004: 0,
    0x005: 0,

    0x101: 0,
    0x102: 0,
    0x103: 0,
    0x104: 0,
    0x105: 0,
    0x106: 0,        
    0x107: 0,
    0x108: 0,
    0x109: 0,
    0x10B: 0,
    0x10C: 0,

    0x580: 0,
    0x581: 0,
    0x242: 1,
    0x243: 1,
    0x244: 1,
    0x245: 1,
    0x246: 1,
    0x247: 1,
    0x24B: 1,
    0x24E: 1,
    0x24F: 0,

    0x600: 0,
    0x601: 0,
    0x602: 0,
    0x603: 0,
    0x604: 0,
    0x605: 0,
    0x606: 0,
    0x610: 0,
    0x611: 0,
    0x612: 0,
    0x613: 0,
    0x614: 0,
    0x615: 0,
    0x616: 0,

    0x620: 0,
    0x630: 0,
    0x631: 0,
    0x632: 0,
    0x633: 0,
    0x640: 0
}

os.system('sudo ifconfig can0 down')
os.system('sudo ifconfig can1 down')
os.system('sudo ip link set can0 type can bitrate 125000')
os.system('sudo ip link set can1 type can bitrate 125000')
os.system('sudo ifconfig can0 txqueuelen 65536')
os.system('sudo ifconfig can1 txqueuelen 65536')
os.system('sudo ifconfig can0 up')
os.system('sudo ifconfig can1 up')

queue: Queue.SimpleQueue[can.Message] = Queue.SimpleQueue()
arr: list[can.Message] = []

def can_msg_cb(msg: can.Message) -> None:
    """Regular callback function. Can also be a coroutine."""
    # for _ in range(80):
    #     list(map(lambda msg: queue.put(msg), CAN_Test_Data))
    queue.put(msg, False)

async def can_loop() -> None:
    """The main function that runs in the loop."""
    logging.info("CAN Loop Started")

    with can.interface.Bus(
        channel = 'can1',
        bustype = 'socketcan',
        bitrate=125000
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

def periodically_send_can():
    p1 = arr.pop()
    msg = bytearray([0x03, 0x10])
    buf = bytearray(p1.arbitration_id.to_bytes(4, "little"))
    # p1.data.reverse()
    if CANIDs[p1.arbitration_id] == 0:
        buf.extend(b'\x00\x00\x00\x00')
    else:
        idx = p1.data[0].to_bytes(4, "little")
        buf.extend(idx)
    data = p1.data[1:8]
    data.reverse()
    data = data.ljust(8, b'\x00')
    buf.extend(data)
    msg.extend(buf)
    #buf.extend(p1.data.ljust(12, b'\x00'))
    #msg.extend(buf)
    
    print(msg)
    s.send(msg)
    logging.debug("Sent CAN Buffer")


async def send_can(s: socket.socket):
    loop = asyncio.get_running_loop()
    while True:
        try:
            while (buf := queue.get(False)):
                arr.append(buf)
        except ClientDisconnectError:
            s = reconnect_socket()
        except Queue.Empty:
            # Left blank intentionally
            # If queue is empty we do nothing but wait for more messages to be sent to us
            await asyncio.sleep(queue_empty_delay) # may be able to remove this line - ask lance?
        await asyncio.sleep(0)

        handle_periodic = loop.call_later(0.000008, asyncio.ensure_future, periodically_send_can) # 120kHz = period of 0.000008 seconds

        
if __name__ == "__main__":
    asyncio.run(can_loop())
