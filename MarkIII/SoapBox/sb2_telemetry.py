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

datafunc = None

class MyTCPHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		global datafunc
		print "Got new IP client."
		try:
			ok = True
			while ok:
				payload = datafunc()
				header = struct.pack("H", len(payload))
				ok = self.request.send(header + payload)
		except:
			print "Lost IP client!"


class MyTcpServer():

	def start(self, host, port, func):
		global datafunc
		datafunc = func
    		self.server = SocketServer.TCPServer((host, port), MyTCPHandler)
		thread.start_new_thread(self.server.serve_forever, ())

	def stop(self):
		self.server.socket.close()

