import socket
import logging  

HOST = '169.254.173.129' # IP of the host for ethernet
PORT = 65432

s = socket.create_connection(address=(HOST, PORT))

def reconnect_socket() -> socket:
    global s
    logging.warning("Client reconnecting...")
    s = socket.create_connection(address=(HOST, PORT))
    return s

class ClientDisconnectError(Exception):
    pass
