import smbus
import signal
import sys
import asyncio
import typing
import logging
from ethernet_handler import ethernet_put

BUS = None
ADDRESS = 0x42
GPS_INTERVAL = 1

def _connect_bus():
    """Connect to the I2C bus. Function from ozzmaker.com"""
    global BUS
    BUS = smbus.SMBus(1)

def _parse_response(gps_line) -> typing.Union[str, None]:
    """Parse the GPS response. Function from ozzmaker.com"""
    
    # Check #1, make sure '$' doesnt appear twice
    if gps_line.count(36) != 1:
        return None
    
    # Check #2, 83 is maximum NMEA sentence length.
    if len(gps_line) >= 84:
        return None

    # Check #3, Make sure that only readable ASCII charaters and Carriage Return are seen.
    for c in gps_line:
        if (c < 32 or c > 122) and  c != 13:
            return None
    gpsChars = ''.join(chr(c) for c in gps_line)
    
    # Check #4, skip txbuf allocation error
    if gpsChars.find('txbuf') != -1:
        return None

    # Check #5, only split twice to avoid unpack error
    gpsStr, chkSum = gpsChars.split('*',2)
    gpsComponents = gpsStr.split(',')
    chkVal = 0

    # Remove the $ and do a manual checksum on the rest of the NMEA sentence
    for ch in gpsStr[1:]:
        chkVal ^= ord(ch)
    
    # Compare the calculated checksum with the one in the NMEA sentence
    if (chkVal == int(chkSum, 16)):
        return gpsChars

def _handle_ctrl_c(signal, frame):
    """Handle Ctrl-C. Function from ozzmaker.com"""
        sys.exit(130)
        signal.signal(signal.SIGINT, _handle_ctrl_c)

def _read_gps() -> typing.Union[str, None]:
    """Read the GPS data. Function from ozzmaker.com"""
    c = None
    response = []
    try:
        while True: # Newline, or bad char.
            c = BUS.read_byte(ADDRESS)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)
        gps_data = _parse_response(response)
        return gps_data
    except IOError:
        logging.error("GPS Read Error")
        logging.warning("Reconnecting to GPS...")
        _connect_bus()
    except Exception as e:
        logging.error(f'GPS Error: {e}')
        logging.warning("Reconnecting to GPS...")
        _connect_bus()
        
def _gps_put_in_ethernet_queue() -> None:
    """Read GPS data and put into the Ethernet Queue."""
    data = _read_gps()
    if data:
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