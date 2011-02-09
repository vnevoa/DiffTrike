#!/usr/bin/python

#    Copyright 2011 Vasco Nevoa.
#
#    This file is part of DiffTrike.
#
#    DiffTrike is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DiffTrike is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DiffTrike. If not, see <http://www.gnu.org/licenses/>.

#
# This implements the Trike's main control application and is directly launchable.
# It depends on python-pygame.
#

#### module imports ####

import os, sys, signal, time, thread
import struct, math
import sb2_joystick, sb2_telemetry
import pygame


#### local classes ####

class inputData():
	def __init__(self):
		jsX = 0
		jsY = 0
		jsB1 = 0
		jsB2 = 0
		jsHatX = 0
		jsHatY = 0
		acBotX = 0
		acBotY = 0
		acTopX = 0
		acTopY = 0

class outputData():
	def __init__(self):
		left = 0
		right = 0
		t_in = 0
		t_proc = 0
		t_out = 0


#### local functions ####

# "kill" signal handler
def handler(signum, frame):
        global ongoing
        ongoing = 0

# callback for the telemetry server
def getstruct():
        sync.acquire()
        return struct.pack("fffffff", o.t_in, o.t_proc, o.t_out, i.jsX, i.jsY, o.right, o.left)


#### main program ####

print "Starting initializations."
t0 = time.time()
i = inputData()
o = outputData()
sync = thread.allocate_lock()
orange = open('/sys/devices/platform/leds_pwm/leds/gta02:orange:power/brightness','w', 0)
blue = open('/sys/devices/platform/leds_pwm/leds/gta02:blue:power/brightness','w', 0)
red = open('/sys/devices/platform/leds-gpio/leds/gta02:red:aux/brightness', 'w', 0)
ongoing = 1

# register termination trap:
signal.signal(signal.SIGTERM, handler)       
signal.signal(signal.SIGINT, handler)

# perform lights test
toggle = 0
red.write("255")
blue.write("255")
orange.write("255")
time.sleep(1)
red.write("0")
blue.write("0")
orange.write("0")

# block other threads
sync.acquire()

# initialize input objects
pygame.init()
stick = sb2_joystick.Joystick()
i.jsX = i.jsY = 0

# initialize output objects
o.left = o.right = 0

# initialize telemetry
t = sb2_telemetry.MyTcpServer()
t.start("192.168.5.202", 11000, getstruct)

# start loop timer (50ms+-10ms)
#pygame.time.set_timer(pygame.USEREVENT, 50)

t1 = time.time()
print "Init=%0.3fs. Entering control loop." % (t1 - t0)

# enter control loop
while ongoing:

	pygame.event.pump()
	# block until timer interval
	#event = pygame.event.wait()
	#if event.type != pygame.USEREVENT:
	#	continue

	t0 = time.time()

	# read inputs
	i.jsX, i.jsY = stick.getXY()
	#io.jsB1, io.jsB2 = stick.getButtons()
	t1 = time.time()

	# get remote control data
	# none yet

	# process data
	o.left  = -i.jsY - i.jsX
	o.right = -i.jsY + i.jsX
	o.left = min(o.left, 1)
	o.left = max(o.left, 0)
	o.right = min(o.right, 1)
	o.right = max(o.right, 0)
	toggle ^= 1
	t2 = time.time()

	# write outputs
	orange.write(str(int(o.left*255.0)))
	blue.write(str(int(o.right*255.0)))
	red.write(str(int(toggle)*255))
	t3 = time.time()

	# set accounting for telemetry
	o.t_in   = (t1 - t0)
	o.t_proc = (t2 - t1)
	o.t_out  = (t3 - t2)

	# allow other threads to work
	if sync.locked() : sync.release()

	# lay off the cpu for a little
	time.sleep(0.040)

# exited control loop, clean up

# stop telemetry server
t.stop()

# close outputs
blue.write('0')                                                                  
blue.close()                                                                     
orange.write('0')                                                                
orange.close()
red.write('0')                                                                
red.close()

# close inputs

