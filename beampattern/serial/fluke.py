import serial
from beampattern.utils.beampattern_exceptions import BeamPatternGeneralError, BeamPatternArgumentError
import numpy

class Fluke(object):
    def __init__(self, port='/dev/ttyUSB0', debug=False):
        self.debug = debug
        self.serial = None
        self.port = port
        self.openport()

    def openport(self):
        self.serial = serial.Serial(self.port,
                                    baudrate=115200,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=3)

    def write(self, text):
        self.serial.write('%s\r\n' % text)

    def read(self):
        ret = self.raw_read()
        try:
            if int(ret) == 0:
                if self.debug:
                    print "No Error"
            else:
                if self.debug:
                    print "Error"
        except:
            pass
        return self.raw_read()

    def raw_read(self):
        ret = ''
        text = self.serial.read(1)
        ret += text
        while text != '\r':
            text = self.serial.read(1)
            if not text:
                break
            ret += text
        return ret.strip('\n').strip('\r')


    def measure(self, nrdgs=2):
        rdg = numpy.zeros(nrdgs, dtype='float')
        for i in range(nrdgs):
            self.write('QM')
            meas = self.read()
            #print meas
            args = meas.split(',')
            if len(args) != 4:
                raise BeamPatternGeneralError("fluke", "Error in measurement")
            else:
                val, unit, state, attribute = args
                val = float(val)
                rdg[i] = val

        return rdg.mean(), rdg.std()
                #return val, "%g %s" % (val, unit)

    def close():
        self.serial.close()

