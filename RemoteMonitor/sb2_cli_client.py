#!/usr/bin/python

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
# This implements a command line interface application that connects to
# the Trike controller via a socket to dump the internal state of the
# controller in real time on the console.
#

import socket, sys, time
sys.path.append("../SoapBoxMkII")
import sb2_input, sb2_output

HOST = "192.168.5.202"
PORT = 11000
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Receive data from the server and shut down
t_1 = time.time()
i = sb2_input.inputData()
o = sb2_output.outputData()
bi = len(i.serialize())
bo = len(o.serialize())
print "input data is %d bytes, output data is %d bytes, total is %d." % (bi, bo, bi+bo)
print
while True:
	received = sock.recv(bi+bo)
	#print "received = %d" % len(received)
	if (len(received) == bi+bo):
		#print len(received), print len(received[0:bi]), len(received[bi:bi+bo])
		i.deserialize(received[0:bi])
		o.deserialize(received[bi:bi+bo])
		t = time.time()
		print "ACC=%0.3f, %0.3f" % (i.accX, i.accY)
		print "GPS=%d, %0.1f, %0.1f" % (i.gpsVld, i.gpsSpd, i.gpsHdng)
		#print "T:%0.3f: L:%d C:%0.3f I:%0.3f P:%0.3f O:%0.3f X:%0.3f Y:%0.3f R:%0.3f L:%0.3f" % \
		#( (t - t_1), len(received), t_cycl, t_in, t_proc, t_out, X, Y, right, left )
		t_1 = t
	else:
		print "failed reception (%d bytes)" % len(received)

sock.close()


