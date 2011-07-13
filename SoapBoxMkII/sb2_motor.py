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
		return t # Celsius

	def getVoltage(self):
		self.device.seek(REG_BAT_VOLTAGE)
		(v,) = struct.unpack('B', self.device.read(1))
		return ((v + 100) / 10.0) # Volt

	def setTorque(self, desired): # [0..1]
		self.device.write(REG_PWM, int(desired*255)) # PWM duty cycle, 0-255

# This is a simple test routine that only runs if this module is 
# called directly with "python sb2_motor.py"

if __name__ == '__main__':

	m1 = I2CMotorBridge('/dev/i2c-0', 0x22)
	m2 = I2CMotorBridge('/dev/i2c-0', 0x23)

	while True:

		print "Motor 1:"

		try:
			t0 = time.time()
			m1.setTorque(0)
			t1 = time.time()
			print " Write=%0.1fms" % (1000*(t1-t0))
		except:
			t1 = time.time()
			print " Write=failed (%0.1fms)" % (1000*(t1-t0))

		try:
			t0 = time.time()
			m1.getRawData()
			t1 = time.time()
			print " Read=%0.1fms" % (1000*(t1-t0))
		except:
			t1 = time.time()
			print " Read=failed (%0.1fms)" % (1000*(t1-t0))

		print "Motor 2:"

                try:
                    	t0 = time.time()
                        m2.setTorque(0)
                        t1 = time.time()
                        print " Write=%0.1fms" % (1000*(t1-t0))
                except:
                       	t1 = time.time()
                        print " Write=failed (%0.1fms)" % (1000*(t1-t0))

                try:
                        t0 = time.time()
                        m2.getRawData()
                        t1 = time.time()
                        print " Read=%0.1fms" % (1000*(t1-t0))
                except:
                        t1 = time.time()
                        print " Read=failed (%0.1fms)" % (1000*(t1-t0))

                print ""

		time.sleep(0.5)
