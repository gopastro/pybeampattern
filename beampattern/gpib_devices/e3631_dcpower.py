#!/usr/bin/env python

from myGpib import Gpib
import types
import time

class E3631A(Gpib):
    """A Gpib helper class for interfacing with the E3631
    Triple output power supply"""
    def __init__(self, name='E3631A', pad=None, sad=0):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.idstr = self.idstring()
        
    def idstring(self):
        "returns ID string"
        return "%s" % self.ask('*IDN?')
    
    def reset(self):
        "Instrument Reset"
        self.write('*RST')

    def set_voltage(self, chan='P25V', voltage=None, current_rating=None):
        if chan not in ('P25V', 'N25V', 'P6V'):
            print "Channel should be one of P25V, N25V or P6V"
            return
        if voltage is None:
            voltage = 'DEF' #sets defaults voltage (0.0 V)
        if current_rating is None:
            current_rating = 'DEF'
        self.write('APPLY %s, %s, %s' % (chan, voltage, current_rating))

    def P25V_set_voltage(self, voltage, current_rating):
        self.set_voltage(chan='P25V', voltage=voltage,
                         current_rating=current_rating)

    def N25V_set_voltage(self, voltage, current_rating):
        self.set_voltage(chan='N25V', voltage=voltage,
                         current_rating=current_rating)
        
    def P6V_set_voltage(self, voltage, current_rating):
        self.set_voltage(chan='P6V', voltage=voltage,
                         current_rating=current_rating)

    def output_status(self):
        """returns output status"""
        op = self.ask("OUTPUT:STATE?")
        if op == '1':
            return "ON"
        else:
            return "OFF"

    def output_off(self):
        self.write("OUTPUT:STATE OFF")

    def output_on(self):
        self.write("OUTPUT:STATE ON")
        
    def measure(self, chan="P25V"):
        if chan not in ("P25V", "N25V", "P6V"):
            print "Wrong channel"
            return
        volt = float(self.ask("MEAS:VOLT:DC? %s" % chan))
        curr = float(self.ask("MEAS:CURR:DC? %s" % chan))
        return (volt, curr)
                
