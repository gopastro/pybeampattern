"""
Beam Pattern Controller for
Unidex11 Motion Controller
Gopal Narayanan <gopal@astro.umass.edu>
"""
#!/usr/bin/env python

from myGpib import Gpib
import types
import time
import gpib
import struct

class Unidex11(Gpib):
    """
    A GPIB helper class for interfacing with the Unidex 11
    motion controller
    """
    def __init__(self, name='unidex11', pad=0, sad=0):
        Gpib.__init__(self, name=name, pad=pad, sad=sad)
        #self.idstr = self.idstring()
        self.step_size_az = 0.1/60. # 0.1 arcmin step size
        self.step_size_el = 0.05/60.
        self.pos_az = 0.0
        self.pos_el = 0.0
        self.limits = (-180.0, 180.0) # az and el position limits
        self.max_feedrate = 20000  #to be safe
        
    def reset(self):
        """
        Instrument Reset
        """
        self.write('C')


    def home(self, axis='X'):        
        """
        Home the axis
        """
        if axis not in ('X', 'Y', 'x', 'y'):
            print "Only X & Y axes can be homed"
            return
        self.write('I H %s *' % axis.upper())
        if axis.upper() == 'X':
            self.pos_az = 0.0
        if axis.upper() == 'Y':
            self.pos_el = 0.0

    def command_in_progress(self):
        """
        Returns True if some command is
        in progress
        """
        i = gpib.serial_poll(self.id)
        motion = struct.unpack('b', i)[0] & 0x20
        if motion:
            return True
        else:
            return False

    def _set_position(self, axis, feedrate, numsteps):
        """
        Given a feedrate and number of steps
        move the stage to the number of steps
        """
        if axis not in ('X', 'Y', 'x', 'y'):
            print "Only X & Y axes can be moved"
            return
        self.write('I %s F%d D%d *' % (axis.upper(), feedrate, numsteps))
        time.sleep(0.25)
        # count = 0
        # while self.command_in_progress():
        #     time.sleep(0.5)
        #     count += 1
        #     if count % 4 == 0:
        #         print "Command in progress, Time = %.2f seconds" % (count*0.5)
        # time.sleep(0.5)
        print "Position set"
            
    def set_azimuth(self, az_command, az_vel):
        """
        moves the stage in azimuth to requested angle 
        with velocity given in degrees/second.
        Feedrate is calculated from this az_vel
        """
        if az_command < self.limits[0] or az_command > self.limits[1]:
            print "Exceeds range of drive"
            return
        numsteps = int((az_command-self.pos_az)/self.step_size_az)
        feedrate = int(abs(az_vel)/self.step_size_az)
        if feedrate > self.max_feedrate:
            feedrate = self.max_feedrate
        self._set_position('X', feedrate, numsteps)
        self.pos_az = az_command

    def set_elevation(self, el_command, el_vel):
        """
        moves the stage in elevation to requested angle 
        with velocity given in degrees/second.
        Feedrate is calculated from this el_vel
        """
        if el_command < self.limits[0] or el_command > self.limits[1]:
            print "Exceeds range of drive"
            return
        numsteps = int((el_command-self.pos_el)/self.step_size_el)
        feedrate = int(abs(el_vel)/self.step_size_el)
        if feedrate > self.max_feedrate:
            feedrate = self.max_feedrate
        self._set_position('Y', feedrate, numsteps)
        self.pos_el = el_command

        
