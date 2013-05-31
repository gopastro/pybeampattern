#!/usr/bin/env python

from myGpib import Gpib
import types
import time

class Analyzer_8757e(Gpib):
    """A Gpib helper class for interfacing with the HP8757E
    Scalar Network Analyzer. Pass through commands to 8350B attached to it.
    """
    def __init__(self, name='8757e', pad=None, sad=0):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        self.format = 0   #normal ascii
        #self.setformat(self.format)
        self.numchannels = int(float(self.ask('OPSP')))
        time.sleep(0.2)
        self.bytesperchan = { 0 : 8,
                              2 : 9
                              }
        self.syn = Gpib('8757e_pt')
        self.write('PT19')
        time.sleep(0.2)
        self.FA = float(self.syn.ask('OPFA'))
        time.sleep(0.1)
        self.FB = float(self.syn.ask('OPFB'))
        time.sleep(0.1)
        self.PL = float(self.syn.ask('OPPL')) #power level
        time.sleep(0.1)
        self.idstr = self.idstring()
        
    def idstring(self):
        "returns ID string"
        return "%s" % self.ask('OI')

    def tracepoints(self, number):
        "Sets the number of tracepoints for a sweep"
        if number in (101,201,401):
            self.write('SP%d' % number)
            self.numchannels = number
        else:
            print "Number of trace points has to be one of (101,201,401)"
    
    def ip(self):
        "Instrument Preset"
        self.write('IP')

    def channel(self, chan, state=True):
        """Selects channel chan, make it active if state
        is True or else turn it off if state is False.
        chan can be a tuple or list. It turns all elements in list to on if
        state is True. If state is set to False, turns first element of list
        or tuple to off and the rest on"""
        if not state:
            if type(chan) == types.TupleType or type(chan) == types.ListType:
                if len(chan) > 1:
                    chan = list(chan)
                    if chan[0] in (1,2):
                        self.write('C%1dC0' % chan[0])
                    else:
                        print "Chan has to be one of 1,2"
                        return
                    for c in chan[1:]:
                        if c in (1,2):
                            self.write('C%1d' % c)
                        else:
                            print "Chan has to be one of 1,2"
                            return                        
                else:
                    print "When turning off a channel, need to send another channel to make active"
                    return
            else:
                print "When turning off a channel, need to send another channel to make active"
                return
        else:
            if type(chan) == types.TupleType or type(chan) == types.ListType:
                for c in list(chan):
                    if c in (1,2):
                        self.write('C%1d' % c)
                    else:
                        print "Chan has to be one of 1,2"
            else:
                if chan in (1,2):
                    self.write('C%1d' % chan)

                
    def setformat(self,num):
        "Sets Ascii formatting of output data"
        if num in (0, 2):
            self.write('FD%d' % num)
            self.format = num
        else:
            print "Supported formats are FD0 and FD2"

    def setFA(self, num):
        "Sets the FA start freq for sweeper"
        fa_gz = num/1.e9
        self.write('PT19')
        self.syn.write("FA%fGZ" % fa_gz)
        time.sleep(0.1)
        self.FA = float(self.syn.ask('OPFA'))
        self.idstr = self.ask('OI')

    def getFA(self):
        self.write('PT19')
        self.FA = float(self.syn.ask('OPFA'))
        self.idstr = self.ask('OI')
        return self.FA

    def setCW(self,num):
        cw_gz = num/1.e9
        self.write('PT19')
        self.syn.write("CW%fGZ" % cw_gz)
        time.sleep(0.1)
        self.CW =float(self.syn.ask('OPCW'))
        self.idstr = self.ask('OI')

    def getCW(self):
        self.write('PT19')
        self.CW = float(self.syn.ask('OPCW'))
        self.idstr = self.ask('OI')
        return self.CW
        
    def setPL(self, num):
        self.write('PT19')
        self.syn.write("PL%fDM" % num)
        time.sleep(0.1)
        self.PL = float(self.syn.ask('OPPL'))
        self.idstr = self.ask('OI')

    def getPL(self):
        self.write('PT19')
        self.PL = float(self.syn.ask('OPPL'))
        self.idstr = self.ask('OI')
        return self.PL
    
    def setFB(self, num):
        "Sets the FB start freq for sweeper"
        fb_gz = num/1.e9
        self.write('PT19')
        self.syn.write("FB%fGZ" % fb_gz)
        time.sleep(0.1)
        self.FB = float(self.syn.ask('OPFB'))
        self.idstr = self.ask('OI')

    def getFB(self):
        self.write('PT19')
        self.FB = float(self.syn.ask('OPFB'))
        self.idstr = self.ask('OI')
        return self.FB    

    def get_learn_string(self):
        self.write('OL')
        self.an_learn = self.readbin(len=150)
        self.write('PT19')
        self.syn.write('OL')
        self.syn_learn = self.syn.readbin(len=90)
        self.idstr = self.ask('OI')
        return (self.an_learn, self.syn_learn)

    def set_learn_string(self,an_learn, syn_learn):
        msg = 'IL'+an_learn
        self.writebin(msg, len(msg))
        self.write('PT19')
        msg = 'IL'+syn_learn
        self.syn.writebin(msg, len(msg))
        self.idstr = self.ask('OI')

    def _getdata(self, text, samples=10):
        self.write('SW1')   #put in sweep mode
        self.write('SW2')   #sweephold mode
        self.write('TS%d' % samples) #take sample number of samples
        time.sleep(1.5)
        self.write('SW1')
        self.write(text)    #ask for the data
        numbytes = self.bytesperchan[self.format]*self.numchannels
        datastr = self.read(len=numbytes)
        data = map(float, datastr.split(','))
        self.write('SW1')        
        return data

    def _getdata_normal(self, text, samples=10):
        """this is more reliable than with TS10
        or whatever for some reason"""
        #self.write('SW1')   #put in sweep mode
        #self.write('SW2')   #sweephold mode
        #self.write('TS%d' % samples) #take sample number of samples
        #time.sleep(1.5)
        #self.write('SW1')
        self.write(text)    #ask for the data
        numbytes = self.bytesperchan[self.format]*self.numchannels
        datastr = self.read(len=numbytes)
        data = map(float, datastr.split(','))
        #self.write('SW1')        
        return data    

    def get_data(self, samples=10):
        return self._getdata_normal('OD', samples)

    def get_memory(self,samples=10):
        return self._getdata_normal('OM', samples)

    def get_normalized(self,samples=10):
        return self._getdata_normal('ON', samples)
    
    def write_memory(self, datastr):
        datastr = 'WM'+datastr
        self.write(datastr)
