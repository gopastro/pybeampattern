#!/usr/bin/env python

from myGpib import Gpib
import types
import time
from beampattern.logging import logger

logger.name = __name__

class HP83620A(Gpib):
    """A Gpib helper class for interfacing with the hp 83620a
    synthesizer
    """
    def __init__(self, name='hp83620a', pad=12, sad=0):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.write('SYST:LANG SCPI') # set language to SCPI
        time.sleep(0.2)
        self.idstr = self.idstring()
        self.mult = self.get_mult()
        logger.debug("ID for synth : %s; Multiplier set to: %s" % (self.idstr, self.mult))
    
    def idstring(self):
        "returns ID string"
        return "%s" % self.ask('*IDN?')
    
    def reset(self):
        "Instrument Reset"
        self.write('*RST')

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
        op = int(self.ask("POWER:STATE?"))
        if op == 1:
            return "ON"
        else:
            return "OFF"

    def output_off(self):
        "Turn RF output off"""
        self.write("POWER:STATE OFF")

    def output_on(self):
        "Turn RF output on"""
        self.write("POWER:STATE ON")

    def get_power_level(self):
        """Get RF power level in dBm"""
        power = float(self.ask('SOUR:POW:LEVEL?'))
        logger.debug("Power = %g dBm" % power)
        return power

    def set_power_level(self, power):
        """Set RF power level in dBm"""
        self.write('SOUR:POW:LEVEL %s' % power)

    def setup_pulse(self):
        """
        These values are specific to beam pattern
        measurements
        """
        self.write('PULS:SOURCE INT') #set to internal pulse source
        time.sleep(0.1)
        self.write('PULS:STATE ON')   #turn on
        time.sleep(0.1)
        self.write('PULM:INT:PER 1 MS')  #set the internal period to 1ms
                                        #so that tuned amp can lock in at 1kHz
        time.sleep(0.1)
        self.write('PULM:INT:WIDTH 500 US')

        
