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
# This implements the Output Data structure used by the main application 
# and the telemetry module.
#

import struct, random

class outputData():
	def __init__(self):

		""" Holds all the necessary system output data """

		self.l_trq = 0 # Left wheel desired torque.
		self.r_trq = 0 # Right wheel desired torque.
		self.t_in = 0  # Time taken during inputs.
		self.t_proc = 0 # Time taken during processing.
		self.t_out = 0  # Time taken during outputs.
		self.t_cycl = 0 # Period of loop cycle.
		self.failed = False # Generic Fail Flag for Output.
		self.failed_r = False # Fail Flag for Right Motor Output.
		self.failed_l = False # Fail Flag for Left Motor Output.
		self.seed = 0 # only for random test data.

	def randomize(self):
		""" fills up the structure with random data. used only for testing. """

		#self.seed = ( random.random() + self.seed ) / 2
		self.seed = random.random()

		self.l_trq = self.seed * 2 - 1 # -1..1 
		self.r_trq = 1 - self.seed * 2 # -1..1
		self.t_in = 0  # 
		self.t_proc = 0 # 
		self.t_out = 0  # 
		self.t_cycl = 0 # 

	def serialize(self):

		""" grabs all the data fields and stuffs them into a string for network communications """

		return struct.pack("ffffffbbb",
		self.t_in, self.t_proc,	self.t_out, self.t_cycl,
		self.l_trq, self.r_trq,
		self.failed, self.failed_r, self.failed_l)


	def deserialize(self, stream):

		""" grabs a binary string and explodes it into all the data fields """

		(self.t_in, self.t_proc, self.t_out, self.t_cycl,
		self.l_trq, self.r_trq,
		self.failed, self.failed_r, self.failed_l) = \
		struct.unpack("ffffffbbb", stream)

# This is a simple test routine that only runs if this module is 
# called directly with "python sb2_output.py"

if __name__ == '__main__':
	i = outputData()
	a = i.serialize()
	print len(a)
	i.deserialize(a)

