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
		self.jsX = 0.0 # Joystick X coordenate [-1..1].
		self.jsY = 0.0 # Joystick Y coordenate [-1..1].
		self.jsB1 = False # Joystick Button 1 state.
		self.jsB2 = False # Joystick Button 2 state.
		self.jsHatX = 0.0 # Joystick Hat X state [-1, 0, 1].
		self.jsHatY = 0.0 # Joystick Hat Y state [-1, 0, 1].
		self.failed_j = False # Fail Flag for Joystick Input.

		# motor bridge data:
		self.motLC = 0.0 # Left Motor Current [A].
		self.motLCclip = False # Left Motor Current Clipping.
		self.failed_l = False # Fail Flag for Left Motor Input.
		self.motRC = 0.0 # Right Motor Current [A].
		self.motRCclip = False # Right Motor Current Clipping.
		self.failed_r = False # Fail Flag for Right Motor Input.
		self.brgLT = 0 # Left Bridge Temperature [C].
		self.brgRT = 0 # Right Bridge Temperature [C].
		self.batLV = 0.0 # Left Battery Voltage [V].
		self.batRV = 0.0 # Right Battery Voltage [V].

		# failure data:
		self.failed = False # Generic Fail Flag for Input.

		self.seed = 0 # for random test data.


	def randomize(self):

		""" fills up the structure with random data. used only for testing. """

		self.seed = random.random() # 0.0 .. 1.0

		# joystick data:
		self.jsX = (self.seed * 2) - 1 # -1..1
		self.jsY = 1 - (self.seed * 2) # -1..1
		self.jsB1 = (self.seed <= 0.50)

		# motor bridge data:
		self.motLC = 20 - (self.seed * 40) # -20..20
		self.motLCclip = (self.seed < 0.25)
		self.motRC = (self.seed * 40) - 20 # -20..20
		self.motRCclip = (self.seed >= 0.25 and self.seed < 0.50) 
		self.brgLT = 10 + int(self.seed * 40) # 10..50
		self.brgRT = 50 - self.brgLT # 10..50
		self.batLV = 22 + int(self.seed * 8) # 22..30
		self.batRV = 30 - (self.batLV - 22) # 22..30

	def serialize(self):

		""" grabs all the data fields and stuffs them into a string for network communications """

		return struct.pack("ff??ff????ffiiff??",
		self.jsX, self.jsY, self.jsB1, self.jsB2, self.jsHatX, self.jsHatY,
		self.failed, self.failed_j, self.failed_r, self.failed_l,
		self.motLC, self.motRC, int(self.brgRT), int(self.brgLT), self.batRV, self.batLV,
		self.motLCclip, self.motRCclip)

	def deserialize(self, stream):

		""" grabs a binary string and explodes it into all the data fields """

		(self.jsX, self.jsY, self.jsB1, self.jsB2, self.jsHatX, self.jsHatY,
		self.failed, self.failed_j, self.failed_r, self.failed_l,
		self.motLC, self.motRC, self.brgRT, self.brgLT, self.batRV, self.batLV,
		self.motLCclip, self.motRCclip) = \
		struct.unpack("ff??ff????ffiiff??", stream)

	def log(self):

		""" grabs all the data fields and returns them in a string """

		return "{0:.2f}".format(self.jsX) + ";" + \
		"{0:.2f}".format(self.jsY) + ";" + \
		"{0:d}".format(self.jsB1) + ";" + \
		"{0:d}".format(self.jsB2) + ";" + \
		"{0:.2f}".format(self.jsHatX) + ";" + \
		"{0:.2f}".format(self.jsHatY) + ";" + \
		"{0:d}".format(self.failed) + ";" + \
		"{0:d}".format(self.failed_j) + ";" + \
\
		"{0:d}".format(self.failed_r) + ";" + \
		"{0:.2f}".format(self.motRC) + ";" + \
		"{0:d}".format(self.brgRT) + ";" + \
		"{0:.2f}".format(self.batRV) + ";" + \
		"{0:d}".format(self.motRCclip) + ";" + \
\
		"{0:d}".format(self.failed_l) + ";" + \
		"{0:.2f}".format(self.motLC) + ";" + \
		"{0:d}".format(self.brgLT) + ";" + \
		"{0:.2f}".format(self.batLV) + ";" + \
		"{0:d}".format(self.motLCclip) + ";"

	def logHeader(self):

		""" returns the names of all the data fields """

		return "jsX; jsY; jsB1; jsB2; jsHatX; jsHatY; failed; failed_j; failed_l; motLC; brgLT; batLV; motLCclip; failed_r; motRC; brgRT; batRV; motRCclip;"

# This is a simple test routine that only runs if this module is 
# called directly with "python sb_input.py"

if __name__ == '__main__':
	i = inputData()
	i.randomize()
	a = i.serialize()
	print len(a)
	i.deserialize(a)
	print i.logHeader()
	print i.log()

