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
import sb2_joystick, sb2_telemetry, sb2_motor
import pygame


#### local classes ####

class inputData():
	def __init__(self):
		jsX = 0 # Joystick X coordenate.
		jsY = 0 # Joystick Y coordenate.
		jsB1 = 0 # Joystick Button 1 state.
		jsB2 = 0 # Joystick Button 2 state.
		jsHatX = 0 # Joystick Hat X state.
		jsHatY = 0 # Joystick Hat Y state.
		acBotX = 0 # Bottom Accelerator X state.
		acBotY = 0 # Bottom Accelerator Y state.
		acTopX = 0 # Top Accelerator X state.
		acTopY = 0 # Top Accelerator Y state.

class outputData():
	def __init__(self):
		l_trq = 0 # Left wheel desired torque.
		r_trq = 0 # Right wheel desired torque.
		t_in = 0  # Time taken during inputs.
		t_proc = 0 # Time taken during processing.
		t_out = 0  # Time taken during outputs.
		t_cycl = 0 # Period of loop cycle.


#### local functions ####

# "kill" signal handler
def handler(signum, frame):
        global ongoing
        ongoing = 0

# callback for the telemetry server
def getstruct():
        sync.acquire()
        return struct.pack("ffffffff", o.t_in, o.t_proc, o.t_out, i.jsX, i.jsY, o.r_trq, o.l_trq, o.t_cycl)


#### main program ####

print "Starting initializations."
t0 = time.time()
i = inputData()
o = outputData()
sync = thread.allocate_lock()
leftM = sb2_motor.I2CMotorBridge('/sys/devices/platform/leds_pwm/leds/gta02:orange:power/brightness')
rightM = sb2_motor.I2CMotorBridge('/sys/devices/platform/leds_pwm/leds/gta02:blue:power/brightness')
red = open('/sys/devices/platform/leds-gpio/leds/gta02:red:aux/brightness', 'w', 0)
ongoing = 1

# register termination trap:
signal.signal(signal.SIGTERM, handler)       
signal.signal(signal.SIGINT, handler)

# perform lights test
toggle = 0
red.write("255")
rightM.setTorque(1)
leftM.setTorque(1)
time.sleep(1)
red.write("0")
rightM.setTorque(0)
leftM.setTorque(0)

# block other threads
sync.acquire()

# initialize input objects
pygame.init()
stick = sb2_joystick.Joystick()
i.jsX = i.jsY = 0

# initialize output objects
o.l_trq = o.r_trq = 0

# initialize telemetry
t = sb2_telemetry.MyTcpServer()
t.start("192.168.5.202", 11000, getstruct)

# start loop timer (50ms+-10ms)
#pygame.time.set_timer(pygame.USEREVENT, 50)

t1 = time.time()
print "Init=%0.3fs. Entering control loop." % (t1 - t0)

# enter control loop
t_1 = t1
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
	o.r_trq  = -i.jsY - i.jsX
	o.r_trq = min(o.r_trq, 1)
	o.r_trq = max(o.r_trq, -1)
	o.l_trq = -i.jsY + i.jsX
	o.l_trq = min(o.l_trq, 1)
	o.l_trq = max(o.l_trq, -1)
	toggle ^= 1
	t2 = time.time()

	# write outputs
	leftM.setTorque(max(0, o.l_trq))
	rightM.setTorque(max(0, o.r_trq))
	red.write(str(int(toggle)*255))
	t3 = time.time()

	# set accounting for telemetry
	o.t_in   = (t1 - t0)
	o.t_proc = (t2 - t1)
	o.t_out  = (t3 - t2)
	o.t_cycl = (t0 - t_1)
	t_1 = t0

	# allow other threads to work
	if sync.locked() : sync.release()

	# lay off the cpu for a little
	time.sleep(0.020)

# exited control loop, clean up

# stop telemetry server
t.stop()

# close outputs
rightM.setTorque(0)
leftM.setTorque(0)
red.write('0')                                                                
red.close()

# close inputs

