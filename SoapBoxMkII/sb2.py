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
import sb2_joystick, sb2_telemetry, sb2_motor, sb2_accelerometers
import pygame

#### global flags

global ongoing
global failed

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
        ongoing = False

# callback for the telemetry server
def getstruct():
        sync.acquire()
        return struct.pack("ffffffff", o.t_in, o.t_proc, o.t_out, i.jsX, i.jsY, o.r_trq, o.l_trq, o.t_cycl)

# "Application alive" LED blinker
def blinkled():
	global ongoing
	global failed
	red = open('/sys/devices/platform/leds-gpio/leds/gta02:red:aux/brightness', 'w', 0)
	toggle = 0
	while ongoing:
		toggle ^= 1
		red.write(str(toggle*255))
		if failed:
			time.sleep(0.1)
		else:
			time.sleep(0.5)
	red.write("0")
	red.close()

#### main program ####

print "Starting initializations."
t0 = time.time()
ongoing = True
failed = False
i = inputData()
o = outputData()
sync = thread.allocate_lock()
# connect to Left motor power bridge:
leftM = sb2_motor.I2CMotorBridge('/dev/i2c-0', 0x22)
leftLed = open('/sys/devices/platform/leds_pwm/leds/gta02:orange:power/brightness','w',0)
# connect to Right motor power bridge:
rightM = sb2_motor.I2CMotorBridge('/dev/i2c-0', 0x22) # we still only have one board, so...
rightLed = open('/sys/devices/platform/leds_pwm/leds/gta02:blue:power/brightness','w',0)
# connect to Bottom accelerometer (the straight one):
accel1 = sb2_accelerometers.NeoAccelerometer('/dev/input/event4')

# register termination trap:
signal.signal(signal.SIGTERM, handler)       
signal.signal(signal.SIGINT, handler)

# launch "alive" thread
thread.start_new_thread(blinkled, ())

# block other threads
sync.acquire()

# initialize input objects
pygame.init()
stick = sb2_joystick.Joystick()
i.jsX = i.jsY = 0
i.failed = i.failed_j = i.failed_r = i.failed_l = False

# initialize output objects
o.l_trq = o.r_trq = 0
o.failed = o.failed_r = o.failed_l = False
leftLed.write("0")
rightLed.write("0")

# initialize telemetry
t = sb2_telemetry.MyTcpServer()
t.start("192.168.5.202", 11000, getstruct)

t1 = time.time()
print "Init=%0.3fs. Entering control loop." % (t1 - t0)

# enter control loop
t_1 = t1
while ongoing:

	pygame.event.pump()

	t0 = time.time()

	# read inputs
	try:
		if not i.failed_j:
			i.jsX, i.jsY = stick.getXY()
			#io.jsB1, io.jsB2 = stick.getButtons()
	except:
		i.failed_j = True
	try:
		if not i.failed_l:
			l = leftM.getRawData()
	except:
		i.failed_l = True
	try:
		if not i.failed_r:
			r = rightM.getRawData()
	except:
		i.failed_r = True
	i.failed = i.failed_r or i.failed_l or i.failed_j
	try:
		a = accel1.getY()
	except:
		pass
	t1 = time.time()

	# process data
	if i.failed or o.failed:
		o.r_trq = 0
		o.l_trq = 0
		failed = True
	else:
		o.r_trq  = -i.jsY - i.jsX
		o.r_trq = min(o.r_trq, 1)
		o.r_trq = max(o.r_trq, 0)
		o.l_trq = -i.jsY + i.jsX
		o.l_trq = min(o.l_trq, 1)
		o.l_trq = max(o.l_trq, 0)
		failed = False
	t2 = time.time()

	# write outputs
	#print "RT=%0.3f LT=%0.3f" % (o.l_trq, o.r_trq)
	try:
		if not o.failed_l:
			leftM.setTorque(o.l_trq)
	except:
		o.failed_l = True
		print "Failed l.setTorque(%0.3f)" % (o.l_trq)
	try:
		if not o.failed_r:
			rightM.setTorque(o.r_trq)
	except:
		o.failed_r = True
		print "Failed r.setTorque(%0.3f)" % (o.r_trq)
	o.failed = o.failed_r or o.failed_l
	if i.failed:
		leftLed.write("20")
		rightLed.write("20")
	if o.failed_r:
		rightLed.write("255")
		if not o.failed_l:
			leftM.setTorque(0)
	if o.failed_l:
		leftLed.write("255")
		if not o.failed_r:
			rightM.setTorque(0)
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
	time.sleep(0.010)

# exited control loop, clean up
print i.failed_j, i.failed_l, i.failed_r
print o.failed_l, o.failed_r

# stop telemetry server
t.stop()


