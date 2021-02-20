#! /usr/bin/env python3 -u

import sys
import time
from datetime import datetime as dt
import serial


dev_path = sys.argv[1]

READ_PPM = bytearray([0xFF, 0xFE, 0x02, 0x02, 0x03])

with serial.Serial(dev_path, 19200, timeout=2) as ser:
    #ser.reset_input_buffer()
    #ser.reset_output_buffer()
    #ser.send_break()
    
    while True:
        ser.write(READ_PPM)
        
        resp = ser.read(5)
        #print(resp)
        assert len(resp) == 5
        assert resp[0] == 0xFF
        assert resp[1] == 0xFA
        assert resp[2] == 0x02
        ts = dt.now().isoformat(timespec='seconds')
        ppm = (resp[3] << 8) + resp[4]
        print(','.join([ts,str(ppm)]))
        time.sleep(5)
