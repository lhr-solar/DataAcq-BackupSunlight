import socket
import logging  

HOST = '169.254.173.129'
PORT = 65432

s = socket.create_connection(address=(HOST, PORT))