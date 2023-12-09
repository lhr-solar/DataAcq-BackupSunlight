import logging
import queue as Queue
import asyncio
from typing import List
import can
from can.notifier import MessageRecipient
from ethernet_handler import ethernet_put


# CAN bus object
bus = can.Bus(
        channel = 'can1',
        bustype = 'socketcan',
        bitrate=125000,
        receive_own_messages=False
    )

# CAN Queue to hold the can messages as they come in
_can_queue = asyncio.Queue()

# CAN IDs that require an index
index_ids = [0x104, 0x105]


def _can_msg_callback(msg: can.Message) -> None:
    '''
    The callback function for the CAN bus. 
    This function will be called to put the CAN message from the interrupt
    into internal CAN queue.
    '''
    _can_queue.put_nowait(msg)


async def _can_put_in_ethernet_queue() -> None:
    '''
    This function will pull CAN messages from the internal CAN queue, process them, 
    and push to the ethernet queue
    '''
    while True:
        # Wait for a CAN message to be put into the queue
        msg = await _can_queue.get()

        # Process the CAN message
        header = bytearray([0x03, 0x10])
        id = msg.arbitration_id 
        # If the message contains an index, grab the index from the first byte of the data
        if id in index_ids:
            idx = msg.data[0].to_bytes(4, "little")
            data = msg.data[1:8].ljust(8, b'\x00')
        # If the message does not contain an index, set the index to 0
        else:
            idx = b'\x00\x00\x00\x00'
            data = msg.data.ljust(8, b'\x00')
        id = bytearray(id.to_bytes(4, "little"))
        packet = header + id + idx + data

        # Push the packet to the ethernet queue
        ethernet_put(packet)

    
async def can_main() -> None:
    '''
    This is the interrupt function for the CAN bus.
    This sets up a notifier to trigger the _can_msg_callback function
    '''
    # Want Reader and Logger
    reader = can.AsyncBufferedReader()
    logger = can.Logger("somefile.asc")

    # We only have 1 listener, the thing that throws the Can msg into the BUS
    listeners: List[MessageRecipient] = [
        _can_msg_callback # Callback Function
    ]

    # Creating Notifer with an explicit loop to use for scheduling of callbacks
    loop = asyncio.get_running_loop()
    notifer = can.Notifier(bus=bus, listeners=listeners, loop=loop) #not sure that "bus" is correct here

    # Start sending the messages
    bus.send(can.Message(arbitration_id=0)) # No clue what this reall does - what is "Message" and "arbiration_id"

    # They "bounced 10 messages", but we want to send more than 10 msgs
    while True:
        # Wait for the next message from Callback Function
        msg = await _can_msg_callback.get_message() # shouldnt this be an Aysnc??
