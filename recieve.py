import os
import can
import asyncio
from typing import List

from can.notifier import MessageRecipient

os.system('sudo ip link set can0 type can bitrate 100000')
os.system('sudo ifconfig can0 up')

# can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')# socketcan_native

def print_message(msg: can.Message) -> None:
    """Regular callback function. Can also be a coroutine."""
    print(msg)


async def main() -> None:
    """The main function that runs in the loop."""

    with can.interface.Bus(  # type: ignore
        channel="can0", bustype='socketcan'
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

        print("Bouncing 10 messages...")
        for _ in range(10):
            # Wait for next message from AsyncBufferedReader
            msg = await reader.get_message()
            print(str(msg))
            # Delay response
            # await asyncio.sleep(0.5)
            # msg.arbitration_id += 1
            # bus.send(msg)

        # Wait for last message to arrive
        await reader.get_message()
        print("Done!")

        # Clean-up
        notifier.stop()
        #os.system('sudo ifconfig can0 down')
# or
# listener.on_message_received(msg)

# Important to ensure all outputs are flushed



if __name__ == "__main__":
    asyncio.run(main())
