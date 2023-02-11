import socket
import logging
import time

HOST = '169.254.240.155'
PORT = 65432


def reconnect_socket(client: socket) -> socket:

    logging.warning("Client disconnect")
    client.close()
    logging.warning("Client reconnecting...")
    return socket.create_connection(address=(HOST, PORT))

class ClientDisconnectError(Exception):
    pass

def sender():
    s = socket.create_connection(address=(HOST, PORT))
    logging.warning("Client starting...")
    s.setblocking(True)
    i = 0
    while True:
        try:
            buf = bytearray([2,2,1,4])
            s.send(buf)
            print(buf)
            time.sleep(1)
            
        except ClientDisconnectError:
            s = reconnect_socket(s)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sender()