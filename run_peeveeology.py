import requests
import datetime
import time
import epics
from functools import partial

from plog.config import rfid_host, rfid_port

DEVICE = 'PV'  # for interfaces CR,SW,NE,BS,BN,PV,UI
DEBUG = True
PV_SERVER = rfid_host + ":" + rfid_port
INIT = True
DOOR_STATE = ['NaN','Open','Closed']
SHUTTER_STATE = ['NaN','Closed','Enabled']
ACCESS_STATE = ['NaN','No Access','Authorised','Open','Error']
KEY_STATE = ['NaN','Removed','Present']

now = datetime.datetime.now()
fnow = now.strftime("%Y-%m-%d %H:%M:%S")
print("%s> Available PV's..." % fnow )
print("Connected to PV's: " )


def onChange(pvname=None, value=None, char_value=None, timestamp=None, enum_list=None, **kw):
    # output data to command line
    now = datetime.datetime.now()
    fnow = now.strftime("%Y-%m-%d %H:%M:%S")
    # print("%s> Data: (%s) (%s) (%s) (%s)" % (fnow, time.ctime(timestamp), pvname, value, enum_list[value]))
    if DEBUG:
        print("%s> Data: (%s) (%s) (%s) (%s)" % ( fnow, time.ctime(timestamp), pvname, value, enum_list[value] ))

    #send data to server
    try:
        if not INIT:
            r = requests.post(PV_SERVER + "/pv/", data={'timestamp': fnow, 'pv': pvname, 'pv_val': enum_list[value], 'source': DEVICE})
            print("%s> %s %s" % (fnow, r.status_code, r.reason))
    except requests.exceptions.RequestException as e:
        now = datetime.datetime.now()
        fnow = now.strftime("%Y-%m-%d %H:%M:%S")
        print("%s> Error: {}".format(e) % fnow)


master_shutter = epics.PV("PP00:MASTER_SHUTTER_ENABLE_STATUS") # Master Shutter status
master_shutter.add_callback(callback=onChange,enum_list=SHUTTER_STATE)
br_state = epics.PV("PP00:LINAC_BR_ACCESS_MODE_STATUS") # BR Status
br_state.add_callback(callback=onChange,enum_list=SHUTTER_STATE)
sr_state = epics.PV("PP00:SR_ACCESS_MODE_STATUS") # SR Status
sr_state.add_callback(callback=onChange,enum_list=SHUTTER_STATE)
sr_sw_key = epics.PV("PP00:SR_SW_LAB_KEY_STATUS") # SR SW Labrynth Door Keys State
sr_sw_key.add_callback(callback=onChange,enum_list=KEY_STATE)
sr_sw_door = epics.PV("PP00:SR_SW_LAB_DOOR_STATUS") # SR SW Labrynth Door State
sr_sw_door.add_callback(callback=onChange,enum_list=DOOR_STATE)
sr_ne_key = epics.PV("PP00:SR_NE_LAB_KEY_STATUS") # SR NE Labrynth Door Keys State
sr_ne_key.add_callback(callback=onChange,enum_list=KEY_STATE)
sr_ne_door = epics.PV("PP00:SR_NE_LAB_DOOR_STATUS") # SR NE Labrynth Door State
sr_ne_door.add_callback(callback=onChange,enum_list=DOOR_STATE)
br_sth_key = epics.PV("PP00:BR_LAB_SOUTH_KEY_STATUS") # Booster Sth Labrynth Door Keys State
br_sth_key.add_callback(callback=onChange,enum_list=KEY_STATE)
br_sth_door = epics.PV("PP00:BR_LAB_SOUTH_DOOR_STATUS") # Booster Sth Labrynth Door State
br_sth_door.add_callback(callback=onChange,enum_list=DOOR_STATE)
br_nth_key = epics.PV("PP00:BR_LAB_NORTH_KEY_STATUS") # Booster Nth Labrynth Door Keys State
br_nth_key.add_callback(callback=onChange,enum_list=KEY_STATE)
br_nth_door = epics.PV("PP00:BR_LAB_NORTH_DOOR_STATUS") # Booster Nth Labrynth Door State
br_nth_door.add_callback(callback=onChange,enum_list=DOOR_STATE)
linac_key = epics.PV("PP00:LINAC_LAB_KEY_STATUS") # Linac Labrynth Door Keys State
linac_key.add_callback(callback=onChange,enum_list=KEY_STATE)
linac_door = epics.PV("PP00:LINAC_LAB_DOOR_STATUS") # Linac Labrynth Door State
linac_door.add_callback(callback=onChange,enum_list=DOOR_STATE)


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
