import socket
from asyncio import Queue

HOST = '169.254.173.129' # IP of the host for ethernet
PORT = 65432

# Establish a socket connection with the host
_s = socket.create_connection(address=(HOST, PORT))

# Create a Ethernet Queue for data to be sent to the host
_eth_queue = Queue()


class ClientDisconnectError(Exception):
    """Raised when the client disconnects."""
    pass

def reconnect_socket():
    """Reconnect to the host."""
    global _s
    logging.warning("Client reconnecting...")
    _s = socket.create_connection(address=(HOST, PORT))

def ethernet_put(packet: bytearray) -> None:
    """Put a packet into the Ethernet Queue."""
    _eth_queue.put_nowait(packet)

async def ethernet_send() -> None:
    """Send packets from the Ethernet Queue to the host."""
    while True:
        # Wait for a packet to be put into the queue
        packet = await _eth_queue.get()

        # Send the packet to the host
        try:
            _s.send(packet)
        except ClientDisconnectError:
            reconnect_socket()