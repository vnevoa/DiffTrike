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
# This module implements the accelerometer data extraction.
# Currently under heavy development.
#

import sys, time, struct, thread

ACC_AXIS_X = 0
ACC_AXIS_Y = 1
ACC_AXIS_Z = 2

class NeoAccelerometer():

	def __init__(self, filename):
		self.buflen = 1 # how many samples to average for each axis.
		self.xSamp = self.ySamp = self.zSamp = 0 # which sample is the current one.
		self.xVals = [ 0 for i in range(self.buflen) ]
		self.yVals = [ 0 for i in range(self.buflen) ]
		self.zVals = [ 0 for i in range(self.buflen) ]
		self.file = open(filename,'rb', 0)
		# start the data pump:
		self.ongoing = True
		thread.start_new_thread(self.readPump, ())

	def __del__(self):
		self.ongoing = False
		self.file.close()

	def getSample(self):
		# get accelerometer sample, separate fields:
		sample = self.file.read(16)
		return struct.unpack('IIhhi', sample) # (time_MS, time_LS, type, code, value).

	def parseSample(self, sample):
		# initialize:
		a_time = a_value = 0
		a_axis = None
		# interpret sample:
		(a_time1, a_time2, a_type, a_code, a_value) = sample
		a_time = a_time2 / 1000.0 + a_time1
		if a_type == 0 :
			# a "synch" event.
			a_axis = None
		if a_type == 3 :
			# a "data" event.
			a_axis = a_code
		return (a_axis, a_time, a_value/1000.0) # mG to G.

	def readPump(self):
		axis = None
		while self.ongoing:
			# get the data from the device:
			(axis, timestamp, value) = self.parseSample(self.getSample())
			# keep the buffers fed:
			if axis == ACC_AXIS_X:
				self.xVals[self.xSamp] = value
				self.xSamp = (self.xSamp + 1) % self.buflen
			if axis == ACC_AXIS_Y:
				self.yVals[self.ySamp] = value
				self.ySamp = (self.ySamp + 1) % self.buflen
			if axis == ACC_AXIS_Z:
				self.zVals[self.zSamp] = value
				self.zSamp = (self.zSamp + 1) % self.buflen

	def getX(self):
		value = 0
		for i in range(self.buflen):
			value += self.xVals[i]
		value /= self.buflen
		return value

	def getY(self):
		value = 0
		for i in range(self.buflen):
			value += self.yVals[i]
		value /= self.buflen
		return value

	def getZ(self):
		value = 0
		for i in range(self.buflen):
			value += self.zVals[i]
		value /= self.buflen
		return value

# This is a simple test routine that only runs if this module is 
# called directly with "python sb2_accelerometer.py"

if __name__ == '__main__':
	#top_acc = NeoAccelerometer('/dev/input/event3'); # top, skewed accelerometer
	bot_acc = NeoAccelerometer('/dev/input/event4'); # bottom, straight accelerometer
	for i in range(50):
		#print bot_acc.parseSample(bot_acc.getSample())
		t0 = time.time()
		X = bot_acc.getX()
		t1 = time.time()
		Y = bot_acc.getY()
		t2 = time.time()
		Z = bot_acc.getZ()
		t3 = time.time()
		print "X=%0.3fG(%0.1fms);  Y=%0.3fG(%0.1fms); Z=%0.3fG(%0.1fms)" % (X, 1000*(t1-t0), Y, 1000*(t2-t1), Z, 1000*(t3-t1))
		time.sleep(0.5)

