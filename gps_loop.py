import socket
from eth_socket import ClientDisconnectError, reconnect_socket
import smbus
import signal
import sys
import queue as Queue
import asyncio
import typing
import logging

BUS = None
address = 0x42
gps_read_interval = 0.03
queue = Queue.SimpleQueue()

def connect_bus():
    global BUS
    BUS = smbus.SMBus(1)
def parse_response(gps_line) -> typing.Union[str, None]:
  if(gps_line.count(36) == 1):                           # Check #1, make sure '$' doesnt appear twice
    if len(gps_line) < 84:                               # Check #2, 83 is maximun NMEA sentenace length.
        char_errors = 0;
        for c in gps_line:                               # Check #3, Make sure that only readiable ASCII charaters and Carriage Return are seen.
            if (c < 32 or c > 122) and  c != 13:
                char_errors+=1
        if (char_errors == 0):#    Only proceed if there are no errors.
            gpsChars = ''.join(chr(c) for c in gps_line)
            if (gpsChars.find('txbuf') == -1):          # Check #4, skip txbuff allocation error
                gpsStr, chkSum = gpsChars.split('*',2)  # Check #5 only split twice to avoid unpack error
                gpsComponents = gpsStr.split(',')
                chkVal = 0
                for ch in gpsStr[1:]: # Remove the $ and do a manual checksum on the rest of the NMEA sentence
                     chkVal ^= ord(ch)
                if (chkVal == int(chkSum, 16)): # Compare the calculated checksum with the one in the NMEA sentence
                     return gpsChars
def handle_ctrl_c(signal, frame):
        sys.exit(130)
#This will capture exit when using Ctrl-C
signal.signal(signal.SIGINT, handle_ctrl_c)
def read_gps(q: Queue.SimpleQueue):
    c = None
    response = []
    try:
        while True: # Newline, or bad char.
            c = BUS.read_byte(address)
            if c == 255:
                return False
            elif c == 10:
                break
            else:
                response.append(c)
        gps_data = parse_response(response)
        if gps_data:
          q.put(gps_data)
    except IOError:
        logging.error("GPS Read Error")
        logging.warning("Reconnecting to GPS...")
        connect_bus()
    except Exception as e:
        logging.error(f'GPS Error: {e}')
        logging.warning("Reconnecting to GPS...")
        connect_bus()

queue_empty_delay = 0.03
async def send_gps(s: socket.socket):
    while True:
        try:
            while (i := queue.get(False)):
                try:
                    msg = bytearray([0x02, 0x10])
                    buf = bytearray(i, "utf-8").rjust(8, b'\x00')
                    msg.extend(buf)
                    
                    print(i)
                    
                    # s.send(buf)
                    logging.debug("Sent GPS Buffer")

                except ClientDisconnectError:
                    s = reconnect_socket(s)
        except Queue.Empty as e:
            await asyncio.sleep(queue_empty_delay)
        await asyncio.sleep(0)
        
async def gps_loop() -> None:
    logging.info("GPS Loop Started")

    connect_bus()
    while True:
        read_gps(queue)
        await asyncio.sleep(gps_read_interval)