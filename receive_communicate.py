import socket
import logging


HOST = ""  # This listens to every interface
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

def connect_socket(s: socket) -> socket:

    logging.warning(f"Server listening on {HOST}")
    s.listen(1)
    (conn, addr) = s.accept()
    logging.warning(f"Server accepted {addr}")
    return conn


def reconnect_socket(server: socket, conn: socket) -> socket:

    logging.warning("Server Disconnected")
    conn.close()
    return connect_socket(server)


class ServerDisconnectError(Exception):
    pass


def receiver():

    s = socket.create_server(address=(HOST, PORT), family=socket.AF_INET)
    logging.warning("Server starting...")
    s.setblocking(True)
    conn = connect_socket(s)
    buf = bytearray(24)
    while True:
        try:
            if conn.recv_into(buf, 2) == 0:
                logging.warning("Empty")
                raise ServerDisconnectError
            print()
            print(buf)
            msgLength = 2#int.from_bytes([buf[1]], "little")
            r = bytearray(msgLength)
            i = 0
            
            while i < msgLength:
                recv_len = conn.recv_into(buf, msgLength + 1 - i)
                if recv_len == 0:
                    logging.warning("Empty Packet")
                    raise ServerDisconnectError
                r[i : recv_len + i] = buf[:recv_len]
                i += recv_len
            print(r)


        except ServerDisconnectError:
            conn = reconnect_socket(s, conn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    receiver()