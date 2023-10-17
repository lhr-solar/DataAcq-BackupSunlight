import socket
import logging

HOST = '100.66.148.34'
PORT = 65432

logging.info("Connecting to host...")
s = socket.create_connection(address=(HOST, PORT))

def reconnect_socket() -> socket:
    global s
    logging.warning("Client reconnecting...")
    s = socket.create_connection(address=(HOST, PORT))
    return s

class ClientDisconnectError(Exception):
    pass
