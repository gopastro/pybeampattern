#!/usr/bin/env python

from myGpib import Gpib
import types
import time

class PowerMeter(Gpib):
    """A Gpib helper class for interfacing with the power meter
    """
    def __init__(self, name='pmeter', pad=None, sad=0):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.idstr = self.idstring()
        
    def idstring(self):
        "returns ID string"
        return "%s" % self.ask('*IDN?')
    
    def reset(self):
        "Instrument Reset"
        self.write('*RST')

    def get_power(self, mode='LN'):
        return float(self.ask(mode))
    
    def get_linear_power(self):
        return self.get_power(mode='LN')

    def get_db_power(self):
        return self.get_power(mode='LG')
        
