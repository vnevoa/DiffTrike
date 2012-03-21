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

import sys, time
sys.path.append("../SoapBoxMkII")
import sb2_input, sb2_output, sb2_gui_data

tele = sb2_gui_data.Telemetry("192.168.5.202", 11000)
print ""
print "Inputs: ", tele.i.logHeader(), "\n"
print "Outputs: ", tele.o.logHeader(), "\n"
time.sleep(0.5)
while tele.connected:
	print "Inputs: ", tele.i.log()
	print "Outputs: ", tele.o.log()
	print ""
	time.sleep(0.5)


