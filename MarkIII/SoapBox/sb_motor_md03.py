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

import struct, time, thread
import i2c_lib

# Bridge controller registers:
REG_COMMAND = 0       #RW, 0:stop, 1:fwd, 2:rev.
REG_STATUS = 1        #RW, b0:accelerating, b1:over-current, b2:over-temperature, b7:busy.
REG_PWM = 2           #RW, PWM, 0..243
REG_ACCELERATION = 3  #RW, 0:fastest
REG_TEMPERATURE = 4   #RO, NTC, 1/1.42 C
REG_CURRENT = 5       #RO, 186=20A
REG_EMPTY1 = 6        #unused
REG_FW_VERSION = 7    #RO

MAX_PWM = 243.0

class I2CMotorBridge():

	def __init__(self, name, filename, address, debug=False):

		self.busy = False	# microprocessor busy
		self.alarm_I = False	# overcurrent alarm
		self.alarm_T = False	# overtemperature alarm
		self.ramping = False	# i'm not there yet
		self.blockings = 0	# i/o fail count
		self.I = 0.0		# current current :)
		self.T = 0.0		# current temperature
		self.torque = 0.0	# desired torque from application
		self.device = i2c_lib.I2CSlave(name, filename, address)
		self.ongoing = False	# i/o thread lifespan control
		self.lastval = 0	# token to check for resets
		self.reset = False	# did the bridge reset?
		self.name = name	# friendly name
		self.debug = debug	# should I speak loudly?

		if self.test():
			self.ongoing = True
			thread.start_new_thread(self.ioPump, ())
		else:
			print "Device initialization failed. [%s]" % self.device.getId()


	def __del__(self):
		if self.ongoing: time.sleep(0.30)


	def test(self):
		try:
			t0 = time.time()
			self.refreshStatus()
			t1 = time.time()
			if self.debug: print "Firmware revision = %d, Read takes %0.1fms" % (self.fw, 1000*(t1-t0))
			return True
		except:
			return False


	def ioPump(self):

		t0 = time.time()
		ops = 0
		busy = 0
		ramping = 0
		clip = 0
		temp = 0
		resets = 0
		max_I = 0.0

		while self.ongoing:

			ops += 1

			# GET status:
			try:
				self.refreshStatus()
				if self.ramping: ramping += 1
				if self.busy: busy += 1
				if self.alarm_I: clip += 1
				if self.alarm_T: temp += 1
				if self.reset: resets += 1
				if self.I > max_I: max_I = self.I
			except:
				self.blockings += 1

			# SET behavior:
			try:
				self.writeTorque()
			except:
				self.blockings += 1

			# PRINT cycle:
			if self.debug:
				t1 = time.time()
				if ((t1 - t0) * 1000) > 1000:
					t0 = t1
					print "%s: \tops/sec = %d" % (self.device.getId(), ops)
					print " \tmax curr = %0.2fA" % max_I
					if self.blockings: print " \tglitches = %d" % self.blockings
					if busy: print " \tbusy = %d" % busy
					if ramping: print " \tramping = %d" % ramping
					if clip: print " \tclip = %d" % clip
					if temp: print " \tt_lim = %d" % temp
					if resets: print " \tresets = %d" % resets
					print "\n"
					ops = 0
					self.blockings = 0
					ramping = 0
					busy = 0
					clip = 0
					temp = 0
					resets = 0
					max_I = 0.0

			# SLEEP:
			time.sleep(0.017) # 20ms -> 50 cycles/sec


	def refreshStatus(self):
		(a, b, c, d, e, f, g, h) = self.getRawData()
		self.busy = b & 0x80     # microprocessor busy
		self.ramping = b & 0x01  # still accelerating last request
		self.alarm_I = b & 0x02  # current limited
		self.alarm_T = b & 0x04  # temperature limited
		self.reset = (c != self.lastval) # last pwm lost => bridge was reset
		self.I = f * 20.0 / 186.0 # Amps
		self.T = (255 - e) * 1.42 # ???
		self.fw = h # firmware revision


	def getCurrent(self):
		return self.I # Ampere


	def getTemperature(self):
		return self.T # Celsius


	def getVoltage(self):
		return (0)  # not possible


	def setTorque(self, desired): # [-1..1]
		self.torque = max(desired, -1.0)
		self.torque = min(desired, 1.0)


	def getRawData(self):
		self.device.seek(0) # seek to beginning of registers.
		data = self.device.read(8)
		return struct.unpack('BBBBBBBB', data) # dump all of them.


	def waitBusy(self):
		busy = True
		max_retries = 100
		t0 = time.time()
		i = 0
		while busy and i < max_retries:
			self.device.seek(REG_STATUS)
			(status,) = struct.unpack('B', self.device.read(1))
			busy = status & 0x80
			i += 1
			if status != 0:
				time.sleep(0.001)
			#	print "status=%x busy=%d" % (status, busy)
		t1 = time.time()
		return 1000 * (t1-t0)


	def writeTorque(self):
		self.device.write(REG_ACCELERATION, 0)
		busy_time = 0.0
		if self.torque < 0.0:
			pwm = int(-self.torque * MAX_PWM)
			self.device.write(REG_PWM, pwm)
			self.device.write(REG_COMMAND, 2)
		else:
			pwm = int(self.torque * MAX_PWM)
			self.device.write(REG_PWM, pwm)
			self.device.write(REG_COMMAND, 1)
		self.lastval = pwm	# save it for reset check
		#busy_time = self.waitBusy()
		#print "wrote torque=%0.2f pwm=%d; Busy %0.2fms" % (self.torque, pwm, busy_time)


# This is a simple test routine that only runs if this module is 
# called directly with "python sb_motor_md03.py"

if __name__ == '__main__':

	m1 = I2CMotorBridge('LEFT', '/dev/i2c-1', 0x58, True)
	m1ok = m1.ongoing
	m2 = I2CMotorBridge('RIGHT', '/dev/i2c-1', 0x5A, True)
	m2ok = m2.ongoing

	pmin = -255
	pmax = 255

	while m1ok or m2ok:

		for i in range(0, pmax+1) + range(pmin, 1):
			print "Setting torque = %0.2f" % (i/255.0)
			if m1ok: m1.setTorque(i/255.0)
			if m2ok: m2.setTorque(i/255.0)
			time.sleep(0.10)
		print ""
		if m1ok: print "temp1=%0.2f C, curr1=%0.2f A" % (m1.getTemperature(), m1.getCurrent())
		if m2ok: print "temp2=%0.2f C, curr2=%0.2f A" % (m2.getTemperature(), m2.getCurrent())
		print ""

	if not m1ok and not m2ok:
		print "no motors found."
