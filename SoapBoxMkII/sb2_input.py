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
# This implements the Input Data structure used by the main application 
# and the telemetry module.
#

import struct, random

class inputData():
	def __init__(self):

		""" Holds all the necessary system input data """

		# joystick data:
		self.jsX = 0 # Joystick X coordenate [-1..1].
		self.jsY = 0 # Joystick Y coordenate [-1..1].
		self.jsB1 = 0 # Joystick Button 1 state [0, 1].
		self.jsB2 = 0 # Joystick Button 2 state [0, 1].
		self.jsHatX = 0 # Joystick Hat X state [-1, 0, 1].
		self.jsHatY = 0 # Joystick Hat Y state [-1, 0, 1].
		self.failed_j = False # Fail Flag for Joystick Input.

		# accelerometer data:
		self.accX = 0.0 # Accelerometer X state [G].
		self.accY = 0.0 # Accelerometer Y state [G].
		self.failed_a = False # Fail Flag for Accelerometer Input.

		# gps data:
		self.gpsSpd = 0.0 # GPS Ground Speed [m/s].
		self.gpsHdng = 0.0 # GPS Heading or Azimuth [deg].
		self.gpsVld = False # GPS has a fix.
		self.failed_g = False # Fail Flag for GPS Input.

		# motor bridge data:
		self.motLC = 0.0 # Left Motor Current [A].
		self.failed_l = False # Fail Flag for Left Motor Input.
		self.motRC = 0.0 # Right Motor Current [A].
		self.failed_r = False # Fail Flag for Right Motor Input.

		# failure data:
		self.failed = False # Generic Fail Flag for Input.

		self.seed = 0 # for random test data.


	def randomize(self):

		""" fills up the structure with random data. used only for testing. """

		self.seed = random.random()

		# joystick data:
		self.jsX = (self.seed * 2) - 1 # -1..1
		self.jsY = 1 - (self.seed * 2) # -1..1

		# accelerometer data:
		self.accX = (self.seed * 4) - 2 # -2..2
		self.accY = 2 - (self.seed * 4) # -2..2

		# gps data:
		self.gpsSpd = self.seed * 50 * 3.6 # km/h
		self.gpsHdng = self.seed * 360 # 0..360
		self.gpsVld = True

		# motor bridge data:
		self.motLC = (self.seed * 40) - 20 # -20..20 
		self.motRC = 20 - (self.seed * 40) # -20..20


	def serialize(self):

		""" grabs all the data fields and stuffs them into a string for network communications """

		return struct.pack("ffbbffffffbbbbbbb",
		self.jsX, self.jsY, self.jsB1, self.jsB2, self.jsHatX, self.jsHatY,
		self.accX, self.accY,
		self.gpsSpd, self.gpsHdng, self.gpsVld,
		self.failed, self.failed_j, self.failed_a, self.failed_g, self.failed_r, self.failed_l)

	def deserialize(self, stream):

		""" grabs a binary string and explodes it into all the data fields """

		(self.jsX, self.jsY, self.jsB1, self.jsB2, self.jsHatX, self.jsHatY,
		self.accX, self.accY,
		self.gpsSpd, self.gpsHdng, self.gpsVld,
		self.failed, self.failed_j, self.failed_a, self.failed_g, self.failed_r, self.failed_l) = \
		struct.unpack("ffbbffffffbbbbbbb", stream)

# This is a simple test routine that only runs if this module is 
# called directly with "python sb2_input.py"

if __name__ == '__main__':
	i = inputData()
	i.randomize()
	a = i.serialize()
	print len(a)
	i.deserialize(a)
	
