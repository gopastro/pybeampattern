from beampattern.logging import logger
from myGpib import Gpib, GpibError
import time
import types
import numpy

logger.name = __name__

class Multimeter(Gpib):
    """A Gpib helper class for interfacing with the HP3457A
    digital multimeter"""
    def __init__(self, name='hp3478a', pad=23, sad=0,
                 asksleep=0.02):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.asksleep = asksleep
        #self.idstr = self.idstring()
        #logger.debug("Multimeter Id: %s" % self.idstr)

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

    def setup_ac(self, nplc=10.0, range=10.0, nrdgs=2, resolution=0.001):
        """Setup for AC operations
        FIXEDZ 1 only for DC
        """
        self.nrdgs = nrdgs
        cmd = 'F2' #AC mode
        cmd += 'R1' #30V range
        cmd += 'Z1'  #autozero On
        cmd += 'N5'  #5digits on
        self.write(cmd)
        time.sleep(self.asksleep)

    def take_readings(self, nrdgs=2):
        self.write('T3')  #single trigger mode
        time.sleep(self.asksleep)
        volt = numpy.zeros(nrdgs, dtype=float)
        for i in range(nrdgs):
            self.trigger()
            time.sleep(self.asksleep)
            rdg = float(self.read())
            volt[i] = rdg
            logger.debug("%d, %s" % (i, rdg))
        self.write('T1')
        time.sleep(self.asksleep)        
        return volt.mean(), volt.std()

    
