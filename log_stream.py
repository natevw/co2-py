#! /usr/bin/env python3 -u

import sys
import time
from datetime import datetime as dt
import serial


dev_path = sys.argv[1]

STREAM_DATA = bytearray([0xFF, 0xFE, 0x01, 0xBD])

with serial.Serial(dev_path, 19200, timeout=90) as ser:
    ser.write(STREAM_DATA)
    while True:
        resp = ser.read(5)
        #print(resp)
        assert len(resp) == 5
        assert resp[0] == 0xFF
        assert resp[1] == 0xFA
        assert resp[2] == 0x02
        ts = dt.now().isoformat(timespec='seconds')
        ppm = (resp[3] << 8) + resp[4]
        print(','.join([ts,str(ppm)]))
