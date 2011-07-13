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
# This module implements the GPS data extraction.
# Currently under heavy development.
#

import sys, time, thread

class NeoGps():

	def __init__(self, filename):
		# initialize data:
		self.lat = self.lon = (0, 0.0, "-") # degrees, minutes, hemisphere.
		self.velocity = (0.0, 0.0) # speed, azimuth.
		self.valid = False
		self.ongoing = True
		# open the device:
		self.file = open(filename,'rb', 0)
		# start the data pump:
		thread.start_new_thread(self.readPump, ())

	def __del__(self):
		self.ongoing = False
		self.file.close()

	def getSample(self):
		# get gps sample, separate fields:
		while (True):
			line = self.file.readline()
			tag = line[0:6]
			if (tag == "$GPRMC"):
				#print line
				fields = line.split(",")
				if (len(fields) == 13):
					if (fields[2] == "A"):
						self.valid = True
						break
					else: 
						self.valid = False
				# else ignore and continue.
		return fields

	def parseSample(self, sample):
		# interpret sample:
		(tag, ts, valid, lat, lath, lon, lonh, knots, bearing, date, magdec, mdh, csum) = sample
		if (bearing == ""): bearing = "0"
		latitude = (int(lat[0:2]), float(lat[2:10]), lath) # degrees, decimal minutes, hemisphere
		longitude = (int(lon[0:3]), float(lon[3:10]), lonh) # degrees, decimal minutes, hemisphere
		velocity = (float(knots)*0.51444444444, float(bearing)) # knots to m/s.
		# convert strings to numbers and adjust scales:
		return (latitude, longitude, velocity)

	def readPump(self):
		while self.ongoing:
			# get the data from the device:
			(self.lat, self.lon, self.vel) = self.parseSample(self.getSample())

	def getPosition(self):
		# get cached latitude and longitude, conveniently packed:
		if self.valid:
			return (self.lat, self.lon)
		else:
			return ((0, 0.0, "-"), (0, 0.0, "-"))

	def getVelocity(self):
		# get cached speed and heading, conveniently packed:
		if self.valid:
			return self.vel
		else:
			return (0.0, 0.0)	

	def isValid(self):
		# get if GPS has a location fix:
		return self.valid

# This is a simple test routine that only runs if this module is 
# called directly with "python sb2_gps.py"

if __name__ == '__main__':
	gps = NeoGps('/dev/ttySAC1');
	while True:
		t0 = time.time()
		p = gps.getPosition()
		t1 = time.time()
		v = gps.getVelocity()
		t2 = time.time()
		i = gps.isValid()
		print "Valid=%d" % i
		print "Lat=%d:%0.3f %s" % (p[0][0],p[0][1],p[0][2])
		print "Lon=%d:%0.3f %s" % (p[1][0],p[1][1],p[1][2])
		print "Vel=%0.2f Az=%0.2f" % (v[0], v[1])
 		print "Tp=%0.1f Tv=%0.1f" % ((t1-t0)*1000, (t2-t1)*1000)
		time.sleep(1)

