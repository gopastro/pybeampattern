#!/usr/bin/env python

from myGpib import Gpib, GpibError
import types
import time
import gpib
import struct
import numpy
import time

from beampattern.utils.beampattern_exceptions import BeamPatternArgumentError

class Analyzer_8510c(Gpib):
    """
    A Gpib helper class for interfacing with the vector network
    analyzer HP8510C and associated pass-through devices
    """
    def __init__(self, name='8510C', pad=None, sad=0,
                 timeout=gpib.T3s):
        Gpib.__init__(self, name=name, pad=pad, sad=sad, 
                      timeout=timeout)
        self.numfrequencies = 0
        self.read_error_count = 0

    def set_cw_frequency_list(self, freqlist):
        """
        Given a list of frequencies (floats in Hz)
        sets the frequency list within the VNA
        """
        self.numfrequencies = len(freqlist)
        # edit the list ; clear the current list
        self.write('EDITLIST; CLEL;')
        for freq in freqlist:
            self.write('SADD; CENT %s GHz; SDON;' % (freq/1.e9))
        # remove duplicates; finish edits
        self.write('DUPD; EDITDONE;')
        self.write('FORM5; OUTPFREL;')
        self.freq_list = self.read_form5()
        
    def readuntil(self, term=''):
        """Read until no more characters"""
        mystr = ''
        readmore = True
        while(readmore):
            try:
                mystr += self.read()
            except GpibError:
                readmore = False
        return mystr

    def read_form5(self, size=None):
        """
        Format 5 data is 4 byte floating point 
        data
        """
        #data = self.readuntil()
        try:
            if size is None:
                data = self.read()
            else:
                data = self.read(size)
            if data[:2] != '#A':
                raise BeamPatternArgumentError("Analyzer_8510C", 
                                               "Form5 data is corrupt")
            num_bytes = struct.unpack('H', data[2:4])[0]
            print "num_bytes : %s; data available; %s" % (num_bytes, len(data[4:]))
            if num_bytes != len(data[4:]):
                return None
            unpack_data = []
            for i in range(num_bytes/4):
                unpack_data.append(struct.unpack('f', data[4+i*4:8+i*4])[0])
            return unpack_data
        except GpibError:
            return None
        
    def initialize_vna(self, freq_list, measure='S22', avg_value = 32):
        """
        Setup the VNA with a requisite frequency list
        and setup single parameter given by measure
        """
        self.set_cw_frequency_list(freq_list)
        self.write('%s;' % measure)
        self.write('REIP;')
        self.write('SINC; SING; AUTO; CONT;')
        self.write('LISFREQ;')
	self.write('AVERON %d;' % avg_value)

    
    def get_freq_data(self):        
        read_again = True
        while(read_again):
            self.write('FORM5; SING; OUTPDATA;')
            time.sleep(0.5)
            # 4*2 for 4bytes times real+imag, +4 for #A and counts
            size = len(self.freq_list)*4*2 + 4
            data = self.read_form5(size)
            if data is not None:
                read_again = False
            else:
                self.read_error_count += 1
        data = numpy.array(data)
        numrows = len(data)/2
        data.shape = (numrows, 2)
        return data[:,0] + 1j*data[:,1]
