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

import os, sys, signal, time, thread, struct, math
import sb2_input, sb2_output, sb2_joystick, sb2_telemetry, sb2_motor, sb2_accelerometers, sb2_gps
import pygame

#### global flags

global ongoing
global failed

#### local functions ####

# "kill" signal handler
def handler(signum, frame):
	""" Handles an operating system signal (kill) and prepares the main app for clean exit """
	global ongoing
	ongoing = False
	time.sleep(3)

# callback for the telemetry server
def getstruct():
	""" Serializes current input and output data and makes them available for telemetry, for example. """
	sync.acquire()
	inp = i.serialize()
	outp = o.serialize()
	data = inp + outp
	#print "Send ", len(inp), "+", len(outp), "=", len(data)
	return data

# "Application alive" LED blinker
def blinkled():
	""" Blinkled function: blinks the red LED """
	global ongoing
	red = open('/sys/devices/platform/leds-gpio/leds/gta02:red:aux/brightness', 'w', 0)
	toggle = 0
	while ongoing:
		toggle ^= 1
		red.write(str(toggle*255))
		time.sleep(0.25)
	red.write("0")
	red.close()

######################################
############ main program ############
######################################

""" Main control application. Implements the control loop (acquire, process, actuate) and serves data for telemetry. """

print "Starting initializations."
t0 = time.time()
ongoing = True
failed = False
i = sb2_input.inputData()
o = sb2_output.outputData()
sync = thread.allocate_lock()

# register termination trap:
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

# launch "alive" thread
thread.start_new_thread(blinkled, ())

# block other threads
sync.acquire()

######################################
# initialize hardware peripherals
######################################

# connect to the usb joystick:
pygame.init()
stick = sb2_joystick.Joystick(0)

# connect to Left motor power bridge:
leftM = sb2_motor.I2CMotorBridge('/dev/i2c-0', 0x22)
leftLed = open('/sys/devices/platform/leds_pwm/leds/gta02:orange:power/brightness','w',0)

# connect to Right motor power bridge:
rightM = sb2_motor.I2CMotorBridge('/dev/i2c-0', 0x23)
rightLed = open('/sys/devices/platform/leds_pwm/leds/gta02:blue:power/brightness','w',0)

# connect to Bottom accelerometer (the straight one):
accel1 = sb2_accelerometers.NeoAccelerometer('/dev/input/event4')

# connect to the GPS receiver:
gps = sb2_gps.NeoGps('/dev/ttySAC1');

# initialize telemetry
t = sb2_telemetry.MyTcpServer()
t.start("192.168.5.202", 11000, getstruct)

t1 = time.time()
print "Init=%0.3fs. Entering control loop." % (t1 - t0)

########################
# enter control loop
########################

t_1 = t1
while ongoing:

	t0 = time.time()

	#########################
	# read inputs
	#########################

	# read joystick:
	pygame.event.pump() # this is essential for joystick updates.
	try:
		i.jsB1, i.jsB2 = stick.getButtons(2)
#		if i.jsB1: # button 1 as dead man's switch.
		i.jsX, i.jsY = stick.getXY()
#		else:
#			i.jsX = i.jsY = 0.0
	except:
		i.failed_j = True

	# read left bridge:
	try:
		i.motLC = leftM.getCurrent()
		i.batLV = leftM.getVoltage()
	except:
		i.failed_l = True

	# read right bridge:
	try:
		i.motRC = rightM.getCurrent()
		i.batRV = leftR.getVoltage()
	except:
		i.failed_r = True

	# read lateral accelerometer:
	try:
		i.accY = accel1.getY()
		i.accX = accel1.getX()
	except:
		i.failed_a = True

	# read Gps:
	try:
		i.gpsVld = gps.isValid()
		(i.gpsSpd, i.gpsHdng) = gps.getVelocity()
	except:
		i.failed_g = True

	i.failed = i.failed_r or i.failed_l or i.failed_j or i.failed_a or i.failed_g

	t1 = time.time()

	############################
	# process data
	############################

	failed = False
	# simple direct mapping...
	o.r_trq  = -i.jsY - i.jsX
	o.r_trq = min(o.r_trq, 1.0)
	o.r_trq = max(o.r_trq, -1.0)
	# simple direct mapping...
	o.l_trq = -i.jsY + i.jsX
	o.l_trq = min(o.l_trq, 1.0)
	o.l_trq = max(o.l_trq, -1.0)

	t2 = time.time()

	############################
	# write outputs
	############################

	#print "RT=%0.3f LT=%0.3f" % (o.l_trq, o.r_trq)

	# write left motor:
	leftLed.write( str(int(255*(0.5+o.l_trq/2.0))) )
	try:
		leftM.setTorque(o.l_trq)
	except:
		o.failed_l = True
		o.glitches_l += 1
		#print "Failed l.setTorque(%0.3f)" % (o.l_trq)

	# write right motor:
	rightLed.write( str(int(255*(0.5+o.r_trq/2.0))) )
	try:
		rightM.setTorque(o.r_trq)
	except:
		o.failed_r = True
		o.glitches_r += 1
		#print "Failed r.setTorque(%0.3f)" % (o.r_trq)

	o.failed = o.failed_r or o.failed_l

	t3 = time.time()

	############################
	# do telemetry
	############################

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
leftLed.write("0")
leftLed.close()
rightLed.write("0")
leftLed.close()

# stop telemetry server
t.stop()
time.sleep(1)
print "Exited."

