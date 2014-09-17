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
REG_COMMAND = 0       #RW, Special functions, see comments below.
REG_STATUS = 1        #RO, b0~b3: heartbeat, b4:over-current, b5:over-temperature, b6:busy, b7:?
REG_PWM = 2           #RW, b7: direction; b0~6: Speed [0, 10..117]
REG_BRIDGETEMP = 3    #RO, controller temperature, raw diode reading, inversely proportional [?]
REG_MOTORTEMP = 4     #RO, motor temperature, raw diode reading, inversely proportional [?]
REG_CURRENT = 5       #RO, motoring current, Real = Read / 10 [A]
REG_BATTVOLTAGE = 6   #RO, controller's power supply voltage, Real = Read / 10 + 10 [V]
REG_FW_VERSION = 7    #RO, firmware version
# REG_COMMAND available commands:
# eCmd_Reset = 0: Turn off all FETs and reinitialize controller pins.
# eCmd_SetI2cAddr = 1: Write I2C address (in REG_CURRENT) to EEPROM (#ifnotdef DISABLE_EEPROM_WRITE)
# eCmd_SetVref = 2: Write ADC Vref (REG_CURRENT * 10) in EEPROM (#ifnotdef DISABLE_EEPROM_WRITE)
# eCmd_GetVref = 3: Get ADC Vref from EEPROM
# eCmd_DoDoublePulseTest = 4: "Double Pulse", REG_PWM = length of 1st pulse [us], REG_CURRENT = length of pause [us] (#ifdef ENABLE_DOUBLE_PULSE)

MAX_PWM = 117.0

class I2CMotorBridge():

	def __init__(self, name, filename, address, debug=False):

		self.busy = False	# microprocessor busy
		self.alarm_I = False	# overcurrent alarm
		self.alarm_T = False	# overtemperature alarm
		self.i2c_ops = 0	# i/o total count
		self.blockings = 0	# i/o fail count
		self.I = 0.0		# current Motoring current :)
		self.T = 0.0		# current Bridge temperature
		self.mT = 0.0		# current Motor temperature
		self.V = 0.0		# current Battery voltage
		self.power = 0.0	# desired power from application
		self.last_pwm = 0	# last effectively written PWM value
		self.device = i2c_lib.I2CSlave(name, filename, address)
		self.ongoing = False	# i/o thread lifespan control
		self.reset = False	# did the bridge reset?
		self.resets = 0		# how many times did the bridge reset?
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
		self.i2c_ops = 0
		busy = 0
		clip = 0
		temp = 0
		self.resets = 0
		max_I = 0.0
		min_V = 100.0

		while self.ongoing:


			# GET status:
			try:
				self.refreshStatus()
				self.blockings = 0
				if self.busy: busy += 1
				if self.alarm_I: clip += 1
				if self.alarm_T: temp += 1
				if self.reset: self.resets += 1
				if self.I > max_I: max_I = self.I
				if self.V < min_V: min_V = self.V
			except:
				self.blockings += 1
			# count all read attempts
			self.i2c_ops += 1

			# SET behavior:
			try:
				self.writePower()
				self.blockings = 0
			except:
				self.blockings += 1
			# count all write attempts
			self.i2c_ops += 1

			# PRINT cycle:
			if self.debug:
				t1 = time.time()
				if ((t1 - t0) * 1000) > 1000:
					t0 = t1
					line = "%s:\n  %d ios;  %3.3f%% fail;" % (self.device.getId(), self.i2c_ops, 100.0*self.blockings/self.i2c_ops)
					line += "  pwm = %d%%;" % (self.power * 100.0)
					line += "  max curr = %2.1f A;" % max_I
					line += "  min volt = %2.1f V;" % min_V
					if clip: line += "  CLIP = %d;" % clip
					if self.resets: line += "  RESETS = %d;" % self.resets
					print line + "\n"
					clip = 0
					self.resets = 0
					max_I = 0.0
					min_V = 100.0

			# SLEEP:
			time.sleep(0.050) # 50ms -> 20 loops per second
			# exit if we fail I/O for 0.1s (10 = 5 R + 5 W)
			#if self.blockings > 10 :
			#	self.ongoing = False



	def refreshStatus(self):

		(a, b, c, d, e, f, g, h) = self.getRawData()
		#print "%s %2x %2x %2x %2x %2x %2x %2x %2x" % (self.name, a, b, c, d, e, f, g, h)
		if h != 26: # counts as a glitch
			raise Exception("I2C garbage!")
		# bridge forgot my order?
		self.reset = (c != self.last_pwm)
		# b = REG_STATUS
		self.alarm_I = b & 0x10  # b4: current limited
		# d = REG_BRIDGETEMP
		self.T = (255.0 - d) # ???
		# e = REG_MOTORTEMP
		self.mT = (255.0 - e) # ???
		# f = REG_CURRENT
		self.I = f / 10.0 # Amp
		# g = REG_BATTVOLTAGE
		self.V = g / 10.0 + 10 # Volt
		# h = REG_FW_VERSION
		self.fw = h # firmware revision


	def getCurrent(self):
		return self.I # Ampere


	def getTemperature(self):
		return self.T # Celsius


	def getMotorTemperature(self):
		return self.mT # Celsius


	def getVoltage(self):
		return self.V # Volt


	def setPower(self, desired): # [-1..1]
		self.power = max(desired, -1.0)
		self.power = min(desired, 1.0)


	def getRawData(self):
		self.device.seek(0) # seek to beginning of registers.
		data = self.device.read(8)
		return struct.unpack('BBBBBBBB', data) # dump all of them.


	def writePower(self):
		# if the IO pump stops, throw the towel.
		if not self.ongoing : 
			raise Exception("No I/O pump!")
		self.last_pwm = int(abs(self.power) * MAX_PWM)
		if self.power < 0 : self.last_pwm |= 0x80 # reverse direction
		inv = int(0xFF & ~self.last_pwm) # binary complement as check
		self.device.write(REG_PWM, inv, self.last_pwm)
		#print "wrote power=%1.2f inv=0x%x pwm=0x%x" % (self.power, inv, self.last_pwm)


# This is a simple test routine that only runs if this module is 
# called directly with "python sb_motor_md03.py"

if __name__ == '__main__':

        mL = I2CMotorBridge('LEFT', '/dev/i2c-1', 0x22, True)
        mLok = mL.ongoing
        mR = I2CMotorBridge('RIGHT', '/dev/i2c-1', 0x23, True)
        mRok = mR.ongoing

        pmin = -int(MAX_PWM/2)
        pmax = int(MAX_PWM/2)

        while mLok or mRok:

                for i in range(0, pmax+1) + range(pmin, 1):
                        #print "Setting power = %d%%" % (100 * i/MAX_PWM)
                        if mLok: mL.setPower(i/MAX_PWM)
                        if mRok: mR.setPower(i/MAX_PWM)
                        #if mLok: print "LEFT  P %3d%%, B.T %3d, M.T %3d, I %2.1f A, U %2.1f V" % (mL.power*100, mL.getTemperature(), mL.getMotorTemperature(), mL.getCurrent(), mL.getVoltage())
                        #if mRok: print "RIGHT P %3d%%, B.T %3d, M.T %3d, I %2.1f A, U %2.1f V" % (mR.power*100, mR.getTemperature(), mR.getMotorTemperature(), mR.getCurrent(), mR.getVoltage())
                        time.sleep(1)
                        if i == MAX_PWM : time.sleep(4.5)
                print ""
                print ""


	if not mLok and not mRok:
		print "no motors found."
