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
# This module implements data handling classes. 
# It depends on PyGame for the Joystick class.
#

import pygame, socket, sb2_input, sb2_output, time, thread
from pygame.joystick import *


class Joystick():
	"""gets data from the joystick"""

	def __init__(self):
		if pygame.joystick.get_count():
			print "Initializing first joystick."
			self.dev = pygame.joystick.Joystick(0)
			self.dev.init()
			self.present = 1
		else:
			self.present = 0

	def getXY(self):
		return ( self.dev.get_axis(0), self.dev.get_axis(1) )


class Telemetry():
	"""gets data from the remote board."""

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.connected = 0
		self.fresh = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(3.0)
		self.i = sb2_input.inputData()
		self.o = sb2_output.outputData()
		self.a = 0
		self.t = time.time()
		self.blackout_histo = Histogram()
		thread.start_new_thread(self.receive, ())

	def receive(self):
		while True:
			try:
				self.sock.connect((self.host, self.port))
				self.connected = 1
				bytes_i = len(self.i.serialize())
				bytes_o = len(self.o.serialize())
				#print bytes_i, bytes_o
				while True:
					received = self.sock.recv(bytes_i + bytes_o)
					self.t_1 = self.t
					self.t = time.time()
					self.blackout_histo.inc(int(1000 * (self.t - self.t_1)))
					self.i.deserialize(received[0:bytes_i])
					self.o.deserialize(received[bytes_i:bytes_i+bytes_o])
					self.fresh = 1
			except:
				self.connected = 0
				self.sock.close()

	def getJoystick(self):
		return (self.i.jsX, self.i.jsY)

	def getTorque(self):
		return (self.o.l_trq, self.o.r_trq, self.i.motLC, self.i.motRC)
    
	def getTimes(self):
		self.fresh = 0
		return (self.o.t_in, self.o.t_proc, self.o.t_out, self.o.t_cycl)

	def getAccel(self):
		return (self.i.accX, self.i.accY)

	def getGps(self):
		return (self.i.gpsVld, self.i.gpsSpd, self.i.gpsHdng)


class DummyTelemetry():
	"""creates dummy data for use in testing."""

	def __init__(self):
		self.connected = 0
		self.fresh = 1
		self.i = sb2_input.inputData()
		self.o = sb2_output.outputData()
		self.t = time.time()
		self.blackout_histo = Histogram()
		thread.start_new_thread(self.receive, ())

	def receive(self):
		while True:
			self.t_1 = self.t
			self.t = time.time()
			self.blackout_histo.inc(int(1000 * (self.t - self.t_1)))
			self.i.randomize()
			self.o.randomize()
			self.fresh = 1
			time.sleep(0.25)

	def getJoystick(self):
		return (self.i.jsX, self.i.jsY)

	def getTorque(self):
		return (self.o.l_trq, self.o.r_trq, self.i.motLC, self.i.motRC)
    
	def getTimes(self):
		self.fresh = 0
		return (self.o.t_in, self.o.t_proc, self.o.t_out, self.o.t_cycl)

	def getAccel(self):
		return (self.i.accX, self.i.accY)

	def getGps(self):
		return (self.i.gpsVld, self.i.gpsSpd, self.i.gpsHdng)


class Histogram():
	"""holds event frequency data."""

	def __init__(self):
		self.data = dict()

	def inc(self, key):
		if key not in self.data:
			self.data[key] = 1
		else:
			self.data[key] = self.data[key] + 1

	def getall(self):
		ks = self.data.keys()
		ks.sort(None, None, True)
		return ((k, self.data[k]) for k in ks)
