#!/usr/bin/python

from optparse import OptionParser
import sys
from beampattern.gpib_devices.hp3457a_multimeter import Multimeter
from beampattern.gpib_devices.unidex11 import Unidex11
from beampattern.gpib_devices.hp83620a import HP83620A
import numpy
import time
import datetime
import pylab


def open_devices(open_unidex=True, open_multi=True,
                 open_synth=True, velocity=1.0,
                 nplc=10, range=10.0, nrdgs=2,
                 mult=4.0):
    uni = None
    multi = None
    syn = None
    if open_unidex:
        try:
            uni = Unidex11()
            uni.reset()
        except:
            print "Unidex11 Not available"
            sys.exit(-2)
    
    if open_multi:
        try:
            multi = Multimeter()
            if multi.idstr != 'HP3457A':
                print "Multimeter ID not right"
                sys.exit(-2)
            print "HP3457A multimeter initialized"
            multi.setup_ac(nplc=nplc, range=range, nrdgs=nrdgs)
        except:
            print "Multimeter not available"
            sys.exit(-2)

    if open_synth:
        try:
            syn = HP83620A()
            syn.set_mult(mult)
        except:
            print "HP83620A not available"
            sys.exit(-2)

    return uni, multi, syn


  
        
if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--xmin", dest="xmin",
                      action="store", type="float",
                      help="start location for scan in degrees")
    parser.add_option("-e", "--xmax", dest="xmax",
                      action="store", type="float",
                      help="stop location for scan in degrees")
    parser.add_option("-i", "--xinc", dest="xinc",
                      action="store", type="float",
                      help="step size for scan in degrees")
    parser.add_option("-a", "--freq", dest="freq",
                      action="store", type="string",
                      help="frequencies of sweep in GHz in comma-separated form")
    parser.add_option("-S", "--nosweep",
                      action="store_true", dest="no_use_synth",
                      default=False,
                      help="Turn this on if you don't want to use synthesizer")
    parser.add_option("-m", "--mult",
                      action="store", type="float",
                      help="Multiplier for freq synthesizer")
    parser.add_option("-H", "--home", 
                      action="store_true", dest="home",
                      default=False,
                      help="Go home on unidex indexer and exit")
    parser.add_option("-N", "--NPLC", dest="nplc",
                      type="float", default=10,
                      help="Number of Power Line cycles for multimeter readings (default %default)")
    parser.add_option("-n", "--nrdgs", dest="nrdgs",
                      type="int", default=3,
                      help="Number of readings for each trigger of multimeter (default %default)")
    parser.add_option("-r", "--range", dest="range",
                      type="float", default=10.0,
                      help="Range for AC Voltage on the Multimeter (default %default)")
    parser.add_option("-f", "--filename",
                      action="store", type="string",
                      dest="filename", default="beamscan.txt",
                      help="Ascii Filename to store data into")

    (options, args) = parser.parse_args()

    if options.home:
        uni, multi, syn = open_devices(open_multi=False, open_synth=False)
        uni.reset()
        uni.home('X')
        print "Going Home"
        sys.exit(0)

