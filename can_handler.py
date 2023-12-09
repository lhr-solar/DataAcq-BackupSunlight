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

# CAN Queue to hold the can messages as they come in
# _can_queue: asyncio.Queue[can.Message] = asyncio.Queue()
_can_queue = asyncio.Queue()

# CAN IDs that require an index
BPS_VOLT_ID = 0x104
BPS_TEMP_ID = 0x105
index_ids = [BPS_VOLT_ID,BPS_TEMP_ID]

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

async def can_main() -> None:
    '''
    This is the interrupt function for the CAN bus.
    This sets up a notifier to trigger the _can_msg_callback function
    '''
    # Creating Notifer with an explicit loop to use for scheduling of callbacks
    # This is necessary because the CAN bus is interrupt driven
    loop = asyncio.get_running_loop()
    # notifier = can.Notifier(bus=bus, listeners=[_can_msg_callback], loop=loop)
    can.Notifier(bus=bus, listeners=[_can_msg_callback], loop=loop)
    while True:
        await asyncio.sleep(1)