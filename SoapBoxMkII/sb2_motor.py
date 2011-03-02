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
# This module implements the electric motor power driver.
# Currently it is a dummy that just lights up LEDs.
#

class I2CMotorBridge():

	def __init__(self, filename):
		self.desiredTorque = 0
		self.file = open(filename,'w', 0)

	def __del__(self):
		close(self.file)

	def setTorque(self, desired):
		self.desiredTorque = desired
		self.file.write(str(int(desired*255)))

	def getTorque(self):
		return self.desiredTorque

	def getSpeed(self):
		return 0
