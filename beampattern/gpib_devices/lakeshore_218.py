#!/usr/bin/env python

from myGpib import Gpib
import types
import time

units_text = {
    0: 'KRDG?',
    1: 'CRDG?',
    }

class Lakeshore(Gpib):
    """A Gpib helper class for interfacing with the Lakeshore 218
    Temperature Monitor"""
    def __init__(self, name='lakeshore', pad=None, sad=0):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.temperature = {}
        self.idstr = self.idstring()
        
    def idstring(self):
        "returns ID string"
        return "%s" % self.ask('*IDN?')
    
    def reset(self):
        "Instrument Reset"
        self.write('*RST')

    def _read_temperature(self, chan=0, text=None):
        if chan == 0:
            reading = self.ask(text)
            for i, val in enumerate(map(float, reading.split(','))):
                self.temperature[i+1] = val
        else:
            reading = self.ask(text+"%1d" % chan)
            self.temperature[chan] = float(reading)
            
    def read_temperature(self, chan=0, units=0):
        """Read temperature for given channel and store it in
        self.temperature.
        chan=0 implies all channels, otherwise specify the chan in
        a number between 1 through 8.
        units = 0 - Kelvin (default)
        units = 1 - Celsius"""
        if chan != 0:
            if chan not in range(1,9):
                print "Not valid channel"
                return None
        self._read_temperature(chan=chan, text=units_text[units])
        return self.temperature

            
                
