'''
This is our Ethernet module. It takes data from the queue that is exposed to ethernet_put,
and whenever populated, takes that data and sends it to the host.
'''

import socket
import logging
from asyncio import Queue

#HOST = '169.254.173.129' # IP of the host for ethernet
HOST = '169.254.57.78'
PORT = 65432

# Establish a socket connection with the host
_socket = socket.create_connection(address=(HOST, PORT))

# Create a Ethernet Queue for data to be sent to the host
# _ethernet_queue = Queue()
_ethernet_queue = None

class ClientDisconnectError(Exception):
    """Raised when the client disconnects."""

def reconnect_socket():
    """Reconnect to the host."""
    global _socket
    logging.warning("Client reconnecting...")
    _socket = socket.create_connection(address=(HOST, PORT))

def ethernet_put(packet: bytearray) -> None:
    """Put a packet into the Ethernet Queue."""
    global _ethernet_queue
    _ethernet_queue.put_nowait(packet)

async def ethernet_send() -> None:
    """Send packets from the Ethernet Queue to the host."""
    global _ethernet_queue
    _ethernet_queue = Queue()
    while True:
        # Wait for a packet to be put into the queue
        packet = await _ethernet_queue.get()

        # Send the packet to the host
        try:
            _socket.send(packet)
            #logging.debug("Packet: %s\n", packet)
        except (ClientDisconnectError, BrokenPipeError):
            reconnect_socket()
        