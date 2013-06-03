from myGpib import Gpib, GpibError
import time
import types
import numpy

class Multimeter(Gpib):
    """A Gpib helper class for interfacing with the HP3457A
    digital multimeter"""
    def __init__(self, name='hp3457a', pad=None, sad=0,
                 asksleep=0.01):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.asksleep = asksleep
        self.idstr = self.idstring()

    def readuntil(self, term=''):
        """Read until termination character"""
        mystr = ''
        numterms = 0
        try:
            s = self.read(len=1)
        except GpibError:
            return mystr
        if s == term:
            numterms += 1
        mystr += s
        while numterms < 2:
            try:
                s = self.read(len=1)
            except GpibError:
                return mystr
            if s == term:
                numterms += 1
            mystr += s
        return mystr

    def askuntil(self, text):
        self.write(text)
        time.sleep(self.asksleep)
        return self.readuntil()

    def idstring(self):
        """Returns ID String"""
        return self.askuntil('ID?')

    def setup_dc(self, nplc=10, range=10.0, nrdgs=2):
        """Setup for DC operations"""
        for command in ('TRIG HOLD', 'FIXEDZ 1', 'DCV %s,AUTO' % range, 
                        'NPLC %s' % nplc, 'NRDGS %d,SYN' % nrdgs):
            self.write(command)
            time.sleep(self.asksleep)
        #self.write('FIXEDZ 1')
        #self.write('DCV 0.03,AUTO') #setup for 30mV range
        #self.write('NPLC 10')       #NPLC 10: corresponding to 0.17s avg
        #self.write('NRDGS 6,SYN')   #six readings ~ 1s total
        #self.write('TRIG HOLD')

    def setup_ac(self, nplc=10, range=10.0, nrdgs=2):
        """Setup for AC operations
        FIXEDZ 1 only for DC
        """
        
        for command in ('TRIG HOLD', 'FIXEDZ 0', 'ACV %s,AUTO' % range, 
                        'NPLC %s' % nplc, 'NRDGS %d,SYN' % nrdgs):
            self.write(command)
            time.sleep(self.asksleep)

    def take_readings(self, nrdgs=2):
        self.write('TRIG HOLD')
        time.sleep(self.asksleep)
        self.trigger()
        volt = numpy.zeros(nrdgs, dtype=float)
        time.sleep(self.asksleep*10)
        for i in range(nrdgs):
            try:
                rdg = self.readuntil()
                print i, rdg
                volt[i] = float(rdg)
            except ValueError:
                volt[i] = 0.0
            time.sleep(self.asksleep)
        #self.write('TRIG AUTO')
        #time.sleep(self.asksleep)
        return volt.mean(), volt.std()

    
