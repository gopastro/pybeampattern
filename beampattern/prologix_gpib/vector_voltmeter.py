import socket
import time
import struct
from prologix_gpib import PrologixGPIB
import numpy

class VectorVoltmeter(object):
    def __init__(self, prologix, gpib_address=15):
        self.prologix = prologix
        self.gpib_address = gpib_address
        self.prologix.set_gpib_address(self.gpib_address)
        self.idstr = self.idstring()

    def write(self, msg, initgpib=True):
        if initgpib:
            self.prologix.set_gpib_address(self.gpib_address)
        self.prologix.write(msg)

    def ask(self, msg, readlen=128, initgpib=True):
        if initgpib:
            self.prologix.set_gpib_address(self.gpib_address)        
        return self.prologix.ask(msg, readlen=readlen)

    def idstring(self):
        """returns ID String"""
        ids = self.ask('*IDN?')
        return ids
    
    def meas_transmission(self, timelen, sleep=0.2):
        self.write('SYST:FORM FP64')
        self.write("AVER:COUN 3", initgpib=False)
        meas = []
        t0 = time.time()
        while (time.time() - t0) < timelen:
            str = self.ask('MEAS? TRAN', initgpib=False)
            ratio = struct.unpack('>d', str[3:11])[0]
            phase = struct.unpack('>d', str[14:])[0]
            meas.append((ratio, phase))
            time.sleep(sleep)
            #print ratio, phase
        return meas

    def measure_transmission_single(self, average=3):
        self.write('SYST:FORM FP64', initgpib=False)
        self.write("AVER:COUN %d" % average, initgpib=False)
        str = self.ask('MEAS? TRAN', initgpib=False)
        ratio = struct.unpack('>d', str[3:11])[0]
        phase = struct.unpack('>d', str[14:])[0]
        return ratio, phase

    def _measure_vector_averaged_transmission(self, average=10):
        self.write('SYST:FORM FP64')
        cmplx = numpy.zeros(average, dtype='complex')
        for i in range(average):
            self.write("AVER:COUN 1", initgpib=False)
            str = self.ask('MEAS? TRAN', initgpib=False)
            ratio = struct.unpack('>d', str[3:11])[0]
            phase = struct.unpack('>d', str[14:])[0]
            cmplx[i] = ratio * numpy.exp(1j* numpy.radians(phase))
            time.sleep(0.010)
        return cmplx

    def measure_vector_averaged_transmission(self, average=10):
        cmplx = self._measure_vector_averaged_transmission(average=average)
        ratio = numpy.abs(cmplx.mean())
        phase = numpy.degrees(numpy.angle(cmplx.mean()))
        return ratio, phase
    
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
            self.write(s, initgpib=False)
            time.sleep(0.010)
        
