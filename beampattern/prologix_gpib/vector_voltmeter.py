import socket
import time
import struct
from prologix_gpib import PrologixGPIB

class VectorVoltmeter(object):
    def __init__(self, prologix, gpib_address=15):
        self.prologix = prologix
        self.gpib_address = gpib_address
        self.prologix.set_gpib_address(self.gpib_address)
        self.idstr = self.idstring()

    def write(self, msg):
        self.prologix.write(msg)

    def ask(self, msg, readlen=128):
        return self.prologix.ask(msg, readlen=readlen)

    def idstring(self):
        """returns ID String"""
        self.prologix.set_gpib_address(self.gpib_address)
        ids = self.ask('*IDN?')
        return ids
    
    def meas_transmission(self, timelen, sleep=0.2):
        self.prologix.set_gpib_address(self.gpib_address)
        self.write('SYST:FORM FP64')
        self.write("AVER:COUN 3")
        meas = []
        t0 = time.time()
        while (time.time() - t0) < timelen:
            str = self.ask('MEAS? TRAN')
            ratio = struct.unpack('>d', str[3:11])[0]
            phase = struct.unpack('>d', str[14:])[0]
            meas.append((ratio, phase))
            time.sleep(sleep)
            #print ratio, phase
        return meas
 
    def setup(self):
        self.prologix.set_gpib_address(self.gpib_address)        
        setup_for_analog_output = ["*RST", 
                                   "DISP:STAT OFF",
                                   "AVER:COUN 3",
                                   "SYST:FORM FP64",
                                   "FORM POL; FORM LIN",
                                   "FREQ:BAND 10",
                                   "TRIG:SOUR BUS",
                                   "SENS TRAN"]
        for s in setup_for_analog_output:
            self.write(s)
            time.sleep(0.010)
        
