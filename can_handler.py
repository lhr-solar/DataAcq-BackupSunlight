'''
This module handles the ingestion of CAN Messages from the bus,
formats them, and outputs them to our internal Ethernet message queue.
The Ethernet module will then send these messages to the host.
'''

import asyncio
import can
from ethernet_handler import ethernet_put

# CAN bus object
bus = can.Bus(
        channel = 'can1',
        bustype = 'socketcan',
        bitrate=125000,
        receive_own_messages=False
    )


# CAN IDs that require an index
BPS_VOLT_ID = 0x104
BPS_TEMP_ID = 0x105
index_ids = [BPS_VOLT_ID,BPS_TEMP_ID]

async def can_main() -> None:
    '''
    This function will pull CAN messages from the internal CAN queue, process them, 
    and push to the ethernet queue
    '''
    # Creating Notifer with an explicit loop to use for scheduling of callbacks
    # This is necessary because the CAN bus is interrupt driven
    _can_queue = asyncio.Queue() # create queue for msgs
    can.Notifier(
        bus=bus, 
        listeners=[
            (lambda x: _can_queue.put_nowait(x)) # listener enqueues messages when they are received
        ], 
        loop= asyncio.get_running_loop() # use main loop
    )

    # Process CAN messages as they come into the queue.
    while True:
        # Wait for a CAN message to be put into the queue
        msg = await _can_queue.get()
        # Process the CAN message
        header = bytearray([0x03, 0x10])
        msg_id = msg.arbitration_id
        # If the message contains an index, grab the index from the first byte of the data
        if msg_id in index_ids:
            idx = msg.data[0].to_bytes(4, "little")
            data = msg.data[1:8].ljust(8, b'\x00')
        # If the message does not contain an index, set the index to 0
        else:
            idx = b'\x00\x00\x00\x00'
            data = msg.data.ljust(8, b'\x00')
        msg_id = bytearray(msg_id.to_bytes(4, "little"))
        packet = header + msg_id + idx + data
        # Push the packet to the ethernet queue
        ethernet_put(packet)
        