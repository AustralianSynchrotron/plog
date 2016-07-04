#!/usr/bin/env python

# A temporary interface script for the card reader attached to the com port,
# this will eventually be moved onto the propeller chip when PoE module
# becomes available and integrated.

from plog.config import facility_code

import serial
import serial.tools.list_ports
import requests

import datetime

DEVICE = 'TEST'  # for interfaces CR,SW,NE,BS,BN,PV,UI
FACILITY = facility_code

def calc_code(hex_string):
    if len(hex_string) != 9:
        return None,None

    bin_rep = bin(int(hex_string,base=16))[2:].zfill(28)
    bin_strip = bin_rep[3:-1]  # strip off the parity bits

    # extract the facility and code id's
    facility = int(bin_strip[:8],2)
    card_id = int(bin_strip[9:],2)

    # if facility not whats expected there may have been a read error
    # this seems to happen very occasionally, return None
    if facility != FACILITY:
        return None,None
    else:
        return facility,card_id


l = sorted(serial.tools.list_ports.comports())
# Display list of serial ports available
now = datetime.datetime.now()
fnow = now.strftime("%Y-%m-%d %H:%M:%S")
print("%s> Available Ports..." % fnow )
for j in range(len(l)):
    print(l[j])

# Connect to the last serial port (may not always be correct - further testing req'd)
port = serial.Serial(l[-1][0], 115200, timeout=1)

print("Connected to Port: %s" % port.name)
print("Waiting for serial Data...")

try:
    while True:
        # read data from serial port, needs to end with new line character
        fetch = port.readline()

        # if serial port sent data
        if fetch:
            res_fac,res_id = calc_code(fetch)

            # output data to command line
            now = datetime.datetime.now()
            fnow = now.strftime("%Y-%m-%d %H:%M:%S")
            print("%s> %s" % (fnow, fetch))

            # if card data (8 chars + \n) then send post request
            if len(fetch) == 9:
                try:
                    r = requests.post("http://localhost:5555/rfid", data={'timestamp':fnow, 'cardID': fetch, 'source': DEVICE})
                    print("%s> %s %s" % (fnow, r.status_code, r.reason))
                except requests.exceptions.RequestException as e:
                    now = datetime.datetime.now()
                    fnow = now.strftime("%Y-%m-%d %H:%M:%S")
                    print("%s> Error: {}".format(e) % fnow)
                    pass

except KeyboardInterrupt:
    port.close()


