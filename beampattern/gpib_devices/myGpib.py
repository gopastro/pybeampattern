#!/usr/bin/env python
import gpib

RQS = (1<<11)
SRQ = (1<<12)
TIMO = (1<<14)


ibsta_dic = {0 : ('DCAS', 'device clear command'),
             1 : ('DTAS', 'device trigger command'),
             2 : ('LACS', 'board is listener'),
             3 : ('TACS', 'board is talker'),
             4 : ('ATN', 'ATN line asserted'),
             5 : ('CIC', 'board is Controller-in-Charge'),
             6 : ('REM', 'board in remote state'),
             7 : ('LOK', 'board in lockout state'),
             8 : ('CMPL', 'I/O Complete'),
             9 : ('EVENT', 'Clear, trigger or interface event'),
             10 : ('SPOLL', 'board is serial polled'),
             11 : ('RQS', 'device has requested service'),
             12 : ('SRQI', 'board asserting SRQ line'),
             13 : ('END', 'I/O operation ended with EOI'),
             14 : ('TIMO', 'I/O or ibwait timed out'),
             15 : ('ERR', 'Error')
             }

GpibError = gpib.GpibError

class Gpib:
    """Three ways to create a Gpib object:
       Gpib('name')
    returns a board or device object, from a name in the config file
       Gpib(board_index)
    returns a board object, with the given board number
       Gpib(board_index, pad[, sad[, timeout[, send_eoi[, eos_mode]]]])
    returns a device object, like ibdev()"""
    
    def __init__(self, name='gpib0', pad=None, sad = 0,
                 timeout = gpib.T10s, send_eoi = 1,
                 eos_mode = 0, eot=True):
        self._own = False
        self.name = None
        if isinstance(name, basestring):
            self.id = gpib.find(name)
            self.name = name
            self._own = True
        elif pad is None:
            self.id = name
        else:
            self.id = gpib.dev(name, pad, sad, timeout, send_eoi, eos_mode)
            self._own = True
        if eot:
            self.eot = True
        else:
            self.eot = False
        if self._own:
            self.get_status()
            
    def __del__(self):
        """automatically close descriptor when instance is deleted"""
        if self._own:
            gpib.close(self.id)

    def __repr__(self):
        mystr = "%s(%d)" % (self.__class__.__name__, self.id)
        if self.name:
            mystr += ": %s" % self.name
        if self._own:
            mystr += "[PAD: %s; SAD: %s; Timeout: %s]" % (self.pad, self.sad, self.tmo)
        return mystr

    def get_status(self):
        self.pad = None
        self.sad = None
        self.tmo = None
        if self._own:
            self.pad = gpib.ask(self.id, gpib.IbaPAD)
            self.sad = gpib.ask(self.id, gpib.IbaSAD)
            self.tmo = gpib.ask(self.id, gpib.IbaTMO)
            
    def write(self,text):
        if self.eot:
            text += "\n"
        gpib.write(self.id, text)
        
    def writebin(self,text,len):
        gpib.writebin(self.id,text,len)

    def read(self,len=512):
        self.res = gpib.read(self.id,len)
        return self.res.replace('\n','').replace('\r','')
    
    def ask(self, text,readlen=512):
        "Send a write and then do a read"
        self.write(text)
        return self.read(len=readlen)

    def readbin(self,len=512):
        self.res = gpib.readbin(self.id,len)
        return self.res

    def clear(self):
        gpib.clear(self.id)
        
    def interface_clear(self):
        gpib.interface_clear(self.id)

    def config(self,option,value):
        self.res = gpib.config(self.id,option,value)
        return self.res

    def wait(self,mask):
        gpib.wait(self.id,mask)
	
    #def rsp(self):
    #    self.spb = gpib.rsp(self.id)
    #    return self.spb

    def trigger(self):
        gpib.trigger(self.id)
        
    #def ren(self,val):
    #    gpib.ren(self.id,val)

    def ibsta(self):
        self.res = gpib.ibsta()
        return self.res

    def ibcnt(self):
        self.res = gpib.ibcnt()
        return self.res

    def timeout(self,value):
        return gpib.timeout(self.id, value)

    def status(self):
        stat = gpib.ibsta()
        statvals = {}
        for key in ibsta_dic:
            if stat & (1 << key): statvals[ibsta_dic[key][0]] = ibsta_dic[key][1]
        return statvals

