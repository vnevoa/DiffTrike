#
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
# This module implements the electric motor driver and data extraction.
#

import struct, time
import i2c_lib

# Bridge controller registers:
REG_COMMAND = 0
REG_STATUS = 1
REG_PWM = 2
REG_DIRECTION = 3
REG_TEMPERATURE = 4
REG_CURRENT = 5
REG_BAT_VOLTAGE = 6
REG_FW_VERSION = 7

class I2CMotorBridge():

	def __init__(self, filename, address):
		self.device = i2c_lib.I2CSlave(filename, address)

	def getRawData(self):
		self.device.seek(0) # seek to beginning of registers.
		return struct.unpack('BBBBBBBB', self.device.read(8)) # dump all of them.

	def getCurrent(self):
		self.device.seek(REG_CURRENT)
		(T,) = struct.unpack('B', self.device.read(1))
		return (T / 10.0) # Ampere

	def getTemperature(self):
		self.device.seek(REG_TEMPERATURE)
		(t,) = struct.unpack('B', self.device.read(1))
		return (t/10.0) # Celsius

	def getVoltage(self):
		self.device.seek(REG_BAT_VOLTAGE)
		(v,) = struct.unpack('B', self.device.read(1))
		return ((v + 100) / 10.0) # Volt

	def setTorque(self, desired): # [-1..1]
		if desired < 0.0:
			self.device.write(REG_DIRECTION, 0)
			desired = -desired
		else:
			self.device.write(REG_DIRECTION, 1)
			#print "t.in=%0.2f t.out=%d" % (desired, int(desired*255))
		self.device.write(REG_PWM, int(desired*255.0)) # PWM duty cycle, 0-255

def init(motor):
	ok = True
	try:
		t0 = time.time()
		motor.setTorque(0)
		t1 = time.time()
		print " Write=%0.1fms" % (1000*(t1-t0))
	except:
		ok = False
		t1 = time.time()
		print " Write=failed (%0.1fms)" % (1000*(t1-t0))
	try:
		t0 = time.time()
		motor.getRawData()
		t1 = time.time()
		print " Read=%0.1fms" % (1000*(t1-t0))
	except:
		ok = False
		t1 = time.time()
		print " Read=failed (%0.1fms)" % (1000*(t1-t0))
	return ok

# This is a simple test routine that only runs if this module is 
# called directly with "python sb2_motor.py"

if __name__ == '__main__':

	m1 = I2CMotorBridge('/dev/i2c-0', 0x22)
	m1ok = True
	m2 = I2CMotorBridge('/dev/i2c-0', 0x23)
	m2ok = True

	m1ok = init(m1)
	m2ok = init(m2)

	pmin = 0
	pmax = 200

	while True:

		print "cycle up..."
		for i in range(pmin, pmax):
			#print "i=%d" % i
			if m1ok: m1.setTorque(i/255.0)
			if m2ok: m2.setTorque(i/255.0)
			time.sleep(0.01)
		print "temp=%d C" % m1.getTemperature()

		print "cycle down..."
		for i in range(pmin, pmax):
			#print "i=%d" % i
			if m1ok: m1.setTorque(-i/255.0)
			if m2ok: m2.setTorque(-i/255.0)
			time.sleep(0.01)
		print "temp=%d C" % m2.getTemperature()

