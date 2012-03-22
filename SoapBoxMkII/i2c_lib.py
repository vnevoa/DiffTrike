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
# This module implements the IIC bus library.
#

import fcntl, struct
import time

IOCTL_I2C_SETSLAVE = 0x0703
IOCTL_I2C_FORCESLAVE = 0x0706

class I2CSlave():

	def __init__(self, filename, address, force=False):
		self.file = open(filename,'r+b', 0)
		if force:
			fcntl.ioctl(self.file, IOCTL_I2C_FORCESLAVE, address)
		else:
			fcntl.ioctl(self.file, IOCTL_I2C_SETSLAVE, address)

	def __del__(self):
		self.file.close()

	def read(self, bytes):
		return self.file.read(bytes)

	def seek(self, register):
		self.file.write(struct.pack('B', register))

	def write(self, register, data):
		self.file.write(struct.pack('BB', register, data))

# This is a simple test routine that only runs if this module is 
# called directly with "python i2c_lib.py"

if __name__ == '__main__':
	print "Dumping PMU interrupt masks..."
	pmu = I2CSlave('/dev/i2c-0', 0x73, True) # 0x73 = PCF50633 power management unit!
	pmu.seek(0x07)
	irq_masks = struct.unpack('BBBBB', pmu.read(5))
	print " INT1MASK = 0x%x" % (irq_masks[0])
	print " INT2MASK = 0x%x" % (irq_masks[1])
	print " INT3MASK = 0x%x" % (irq_masks[2])
	print " INT4MASK = 0x%x" % (irq_masks[3])
	print " INT5MASK = 0x%x" % (irq_masks[4])
	print ""
