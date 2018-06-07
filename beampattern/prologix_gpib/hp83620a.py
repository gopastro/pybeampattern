import socket
import time
import struct
from prologix_gpib import PrologixGPIB

class HP83620A(PrologixGPIB):
    def __init__(self, prologix, gpib_address=12):
        self.prologix = prologix
        self.gpib_address = gpib_address
        self.prologix.set_gpib_address(self.gpib_address)
        self.idstr = self.idstring()        

    def write(self, msg):
        self.prologix.set_gpib_address(self.gpib_address)        
        self.prologix.write(msg)

    def ask(self, msg, readlen=128):
        self.prologix.set_gpib_address(self.gpib_address)        
        return self.prologix.ask(msg, readlen=readlen)

    def idstring(self):
        """returns ID String"""
        self.prologix.set_gpib_address(self.gpib_address)
        ids = self.ask('*IDN?')
        return ids
    
    def get_mult(self):
        """Get frequency multiplier"""
        self.mult = float(self.ask('FREQ:MULT?'))
        return self.mult

    def set_mult(self, mult=None):
        """Set frequency multiplier"""
        if mult is not None:
            self.mult = mult
        self.write('FREQ:MULT %s' % self.mult)

    def get_freq(self):
        """Get current CW frequency"""
        return float(self.ask('FREQ:CW?'))
    
    def set_freq(self, freq):
        """Set CW frequency in Hz"""
        if freq<1e9:
            fstr = "%s MHz" % (freq/1.e6)
        else:
            fstr = "%s GHz" % (freq/1.e9)
        self.write('FREQ:CW %s' % fstr)

    def output_status(self):
        """returns output status of RF signal"""
        op = int(self.ask("OUTPUT:STATE?"))
        if op == 1:
            return "ON"
        else:
            return "OFF"
        
    def output_off(self):
        "Turn RF output off"""
        self.write("OUTPUT:STATE OFF")

    def output_on(self):
        "Turn RF output on"""
        self.write("OUTPUT:STATE ON")

    def get_power_level(self):
        """Get RF power level in dBm"""
        power = float(self.ask('SOUR:POW:LEVEL?'))
        print "Power = %g dBm" % power
        return power
                                        
    def set_power_level(self, power):
        """Set RF power level in dBm"""
        self.write('SOUR:POW:LEVEL %s' % power)
        
