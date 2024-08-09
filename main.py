from gps_handler import gps_main
from can_handler import can_main
from ethernet_handler import ethernet_send

import asyncio, logging


async def main():
    await asyncio.gather(
        gps_main(),
        can_main(),
        ethernet_send()
    )

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)

    logging.info("Connecting to host...")
    asyncio.run(main())
    