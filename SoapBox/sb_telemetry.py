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
# This module implements the controller's telemetry endpoint.
# It depends on python-netclient.
#

import SocketServer
import thread, struct

getfunc = setfunc = None

class MyTCPHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		global getfunc
		global setfunc
		print "Got new IP client."
		try:
			ok = True
			while ok:
				# SEND status
				payload = getfunc()
				header = struct.pack("H", len(payload))
				ok = self.request.send(header + payload)
				# RECV instructions
				remdata = self.request.recv(12)  # TODO: remote.getlen() or something
				setfunc(remdata)
		except:
			print "Lost IP client!"


class MyTcpServer():

	def start(self, host, port, getp, setp):
		global getfunc
		getfunc = getp
		global setfunc
		setfunc = setp
    		self.server = SocketServer.TCPServer((host, port), MyTCPHandler)
		thread.start_new_thread(self.server.serve_forever, ())

	def stop(self):
		self.server.socket.close()

