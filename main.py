from can_loop import can_loop, send_can
from gps_loop import gps_loop, send_gps
from eth_socket import s

import asyncio, logging

async def eth_socket_loop():
    await asyncio.gather(send_can(s), send_gps(s))

async def main():
    await asyncio.gather(eth_socket_loop(), can_loop(), gps_loop())

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)

    logging.info("Connecting to host...")
    asyncio.run(main())