import requests
import datetime
import time
import epics

from plog.config import rfid_host, rfid_port

DEVICE = 'PV'  # for interfaces CR,SW,NE,BS,BN,PV,UI
DEBUG = True
PV_SERVER = rfid_host + ":" + rfid_port
INIT = True

now = datetime.datetime.now()
fnow = now.strftime("%Y-%m-%d %H:%M:%S")
print("%s> Available PV's..." % fnow )
print("Connected to PV's: " )


def onChange(pvname=None, value=None, char_value=None, timestamp=None, **kw):
    # output data to command line
    now = datetime.datetime.now()
    fnow = now.strftime("%Y-%m-%d %H:%M:%S")
    if DEBUG:
        print("%s> Data: (%s) (%s) (%s)" % ( fnow, time.ctime(timestamp), pvname, char_value ))

    #send data to server
    try:
        if not INIT:
            r = requests.post(PV_SERVER + "/pv/", data={'timestamp': fnow, 'pv': pvname, 'pv_val': char_value, 'source': DEVICE})
            print("%s> %s %s" % (fnow, r.status_code, r.reason))
    except requests.exceptions.RequestException as e:
        now = datetime.datetime.now()
        fnow = now.strftime("%Y-%m-%d %H:%M:%S")
        print("%s> Error: {}".format(e) % fnow)


master_shutter = epics.PV("PP00:MASTER_SHUTTER_ENABLE_STATUS", callback=onChange) # Master Shutter status
br_state = epics.PV("PP00:LINAC_BR_ACCESS_MODE_STATUS",callback=onChange) # BR Status
sr_state = epics.PV("PP00:SR_ACCESS_MODE_STATUS",callback=onChange) # SR Status
sr_sw_key = epics.PV("PP00:SR_SW_LAB_KEY_STATUS",callback=onChange) # SR SW Labrynth Door Keys State
sr_sw_door = epics.PV("PP00:SR_SW_LAB_DOOR_STATUS",callback=onChange) # SR SW Labrynth Door State
sr_ne_key = epics.PV("PP00:SR_NE_LAB_KEY_STATUS",callback=onChange) # SR NE Labrynth Door Keys State
sr_ne_door = epics.PV("PP00:SR_NE_LAB_DOOR_STATUS",callback=onChange) # SR NE Labrynth Door State
br_sth_key = epics.PV("PP00:BR_LAB_SOUTH_KEY_STATUS",callback=onChange) # Booster Sth Labrynth Door Keys State
br_sth_door = epics.PV("PP00:BR_LAB_SOUTH_DOOR_STATUS",callback=onChange) # Booster Sth Labrynth Door State
br_nth_key = epics.PV("PP00:BR_LAB_NORTH_KEY_STATUS",callback=onChange) # Booster Nth Labrynth Door Keys State
br_nth_door = epics.PV("PP00:BR_LAB_NORTH_DOOR_STATUS",callback=onChange) # Booster Nth Labrynth Door State
linac_key = epics.PV("PP00:LINAC_LAB_KEY_STATUS",callback=onChange) # Linac Labrynth Door Keys State
lniac_door = epics.PV("PP00:LINAC_LAB_DOOR_STATUS",callback=onChange) # Linac Labrynth Door State
zone1 = epics.PV("PP00:SEARCH_ZONE1_STATUS",callback=onChange) # Zone 1 Search State
zone2 = epics.PV("PP00:SEARCH_ZONE2_STATUS",callback=onChange) # Zone 2 Search State
zone3 = epics.PV("PP00:SEARCH_ZONE3_STATUS",callback=onChange) # Zone 3 Search State
zone4 = epics.PV("PP00:SEARCH_ZONE4_STATUS",callback=onChange) # Zone 4 Search State
zone5 = epics.PV("PP00:SEARCH_ZONE5_STATUS",callback=onChange) # Zone 5 Search State
zone6 = epics.PV("PP00:SEARCH_ZONE6_STATUS",callback=onChange) # Zone 6 Search State

print("Waiting for PV Data Callbacks to Connect...")
time.sleep(10)

try:
    INIT = None # don't send data during callback registration, now resume normal operation
    now = datetime.datetime.now()
    fnow = now.strftime("%Y-%m-%d %H:%M:%S")
    print("%s> Waiting for PV Data onChange trigger..." % fnow)
    while True: # Just chill and wait for callbacks to work their magic
        time.sleep(0.1)

except KeyboardInterrupt:
    exit(1)
