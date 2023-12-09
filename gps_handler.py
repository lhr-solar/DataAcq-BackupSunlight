import smbus
import signal
import sys
import asyncio
import typing
import logging
from ethernet_handler import ethernet_put

i2c_bus = smbus.SMBus(1) # I2C bus for GPS Shield
ADDRESS = 0x42 # GPS Shield I2C Address
GPS_INTERVAL = 1 # Polling frequency in seconds

def _connect_bus():
    """Connect to the I2C bus. Function from ozzmaker.com"""
    global i2c_bus
    i2c_bus = smbus.SMBus(1)

def _parse_response(gps_line) -> typing.Union[str, None]:
    """Parse the GPS response."""

    # Check #1, make sure '$' doesnt appear twice
    if gps_line.count(36) != 1:
        return None

    # Check #2, 83 is maximum NMEA sentence length.
    if len(gps_line) >= 84:
        return None

    # Check #3, Make sure that only readable ASCII charaters and Carriage Return are seen.
    valid_chars = set(range(32,123)).union({13})
    if not all(c in valid_chars for c in gps_line):
        return None

    gps_chars = ''.join(chr(c) for c in gps_line)

    # Check #4, skip txbuf allocation error
    if 'txbuf' in gps_chars:
        return None

    # Check #5, only split twice to avoid unpack error
    gps_str, check_sum = gps_chars.split('*',2)

    # Remove the $ and do a manual checksum on the rest of the NMEA sentence
    check_val = 0
    for ch in gps_str[1:]:
        check_val ^= ord(ch)

    # Compare the calculated checksum with the one in the NMEA sentence
    if check_val == int(check_sum, 16):
        return gps_chars

def _handle_ctrl_c(signal, frame):
    """Handle Ctrl-C."""
    sys.exit(130)
signal.signal(signal.SIGINT, _handle_ctrl_c)

def _read_gps() -> typing.Union[str, None]:
    """Read the GPS data."""
    BAD_CHAR = 0xFF
    NEWLINE = 0x0A
    c = None
    response = []
    try:
        while True: # Newline, or bad char.
            c = i2c_bus.read_byte(ADDRESS)
            if c == BAD_CHAR:
                return None
            if c == NEWLINE:
                break
            response.append(c)
        gps_data = _parse_response(response)
        return gps_data
    except Exception as e:
        logging.error('GPS Error: %s', e)
        logging.warning("Reconnecting to GPS...")
        _connect_bus()

def _gps_put_in_ethernet_queue() -> None:
    """Read GPS data and put into the Ethernet Queue."""
    data = _read_gps()
    if data is None:
        return
    header = bytearray([0x02, 0x10])
    data = bytearray(data, "utf-8").rjust(8, b'\x00')
    packet = header + data
    ethernet_put(packet)

async def gps_main() -> None:
    """Connect to GPS over I2C and add data to Ethernet Queue periodically."""

    logging.info("GPS Loop Started")
    _connect_bus()
    # Read GPS data and add to Ethernet Queue once a second
    while True:
        _gps_put_in_ethernet_queue()
        logging.debug("GPS data added to queue")
        await asyncio.sleep(GPS_INTERVAL)