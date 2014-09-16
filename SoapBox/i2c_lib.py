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

IOCTL_I2C_SETTIMEOUT = 0x0702
IOCTL_I2C_SETSLAVE = 0x0703
IOCTL_I2C_FORCESLAVE = 0x0706

class I2CSlave():

	def __init__(self, name, filename, address, force=False):
		self.file = open(filename,'r+b', 0)
		self.name = filename
		self.username = name
		self.address = address
		if force:
			fcntl.ioctl(self.file, IOCTL_I2C_FORCESLAVE, address)
		else:
			fcntl.ioctl(self.file, IOCTL_I2C_SETSLAVE, address)
		fcntl.ioctl(self.file, IOCTL_I2C_SETTIMEOUT, 10) #100ms

	def __del__(self):
		self.file.close()

	def read(self, bytes):
		return self.file.read(bytes)

	def seek(self, register):
		self.file.write(struct.pack('B', register))

	def write(self, register, byte1, byte2):
		self.file.write(struct.pack('BBB', register, byte1, byte2))

#	def write(self, register, byte):
#		self.file.write(struct.pack('BB', register, byte))

	def getId(self):
		return self.username + ":" + self.name + ":" + hex(self.address)

# This is a simple test routine that only runs if this module is 
# called directly with "python i2c_lib.py"

if __name__ == '__main__':
	dev = I2CSlave("DUTx32", '/dev/i2c-1', 0x23, True)

	# positive check: write 0 with correct inverted
	print "FETs OFF"
	dev.write(2, 0xff, 0)
	dev.seek(0)
	data = struct.unpack('BBBBBBBB', dev.read(8))
	print "0xFF,0x00:  0x%x 0x%x 0x%x 0x%x 0x%x 0x%x 0x%x 0x%x" % (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
	time.sleep(3)

	# negative check: write 1 with wrong inverted
	print "FETs still OFF"
	dev.write(2, 0xff, 1)
	dev.seek(0)
	data = struct.unpack('BBBBBBBB', dev.read(8))
	print "0xFF,0x01:  0x%x 0x%x 0x%x 0x%x 0x%x 0x%x 0x%x 0x%x" % (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
	time.sleep(3)

	# positive check: write 1 with good inverted
	print "FETs now ON"
	dev.write(2, 0xfe, 1)
	dev.seek(0)
	data = struct.unpack('BBBBBBBB', dev.read(8))
	print "0xFE,0x01:  0x%x 0x%x 0x%x 0x%x 0x%x 0x%x 0x%x 0x%x" % (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
