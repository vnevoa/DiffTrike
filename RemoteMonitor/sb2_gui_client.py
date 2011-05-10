#!/usr/bin/env python

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
# This implements a graphical user interface application that connects to
# the Trike controller via a socket to monitor the internal state of the
# controller in real time. It requires PyGame.
#

import sys, os, math, pygame, thread, socket, struct, time
import sb2_input, sb2_output
from pygame.locals import * 
from pygame.gfxdraw import *
from pygame.joystick import *
from pygame.font import *

class Text():
	def __init__(self, txt, x, y, fcolor=(255,255,255), bcolor=(0,0,0)):
		self.font = pygame.font.SysFont("", 24)
		self.sf = self.font.render(txt, 0, fcolor, bcolor)
		self.x = x
		self.y = y

class Window():
	"""main window behaviour"""
	def __init__(self, fillcolor=(0, 0, 0)):
		self.color = fillcolor
		pygame.display.set_mode((0,0)) #, pygame.FULLSCREEN) 
		pygame.display.set_caption('SoapBox Mark II Control GUI')
		pygame.mouse.set_visible(0)
		self.sf = pygame.display.get_surface()
		self.width, self.height = self.sf.get_size()
		self.sf.fill(self.color)
		self.txt = []

	def write(self, text, x, y):
		txt = Text(text, x, y)
		self.txt.append(txt)
		(h, v) = txt.sf.get_size()
		return (x + h, y + v)

	def redraw(self):
		self.sf.fill(self.color)
		while (len(self.txt)):
			txt = self.txt.pop()
			self.sf.blit(txt.sf, (txt.x, txt.y))

class Sights():
	"""draws the targeting sights"""
	def __init__(self, size=250, color=(255,0,0)):
		self.color = color
		self.size = size

	def draw(self, bg):
		p1 = ( (bg.width - self.size)/2, (bg.height - self.size)/2 )
		p2 = ( (bg.width + self.size)/2, (bg.height - self.size)/2 )
		p3 = ( (bg.width - self.size)/2, (bg.height + self.size)/2 )
		p4 = ( (bg.width + self.size)/2, (bg.height + self.size)/2 )
		pygame.draw.line( bg.sf, self.color, p1, p2 )
		pygame.draw.line( bg.sf, self.color, p2, p4 )
		pygame.draw.line( bg.sf, self.color, p4, p3 )
		pygame.draw.line( bg.sf, self.color, p3, p1 )
		p5 = ( bg.width/2, -0.05*self.size + (bg.height - self.size)/2 )
		p6 = ( bg.width/2,  0.05*self.size + (bg.height + self.size)/2 )
		p7 = ( -0.05*self.size + (bg.width - self.size)/2, bg.height/2 )
		p8 = (  0.05*self.size + (bg.width + self.size)/2, bg.height/2 )
		pygame.draw.line( bg.sf, self.color, p5, p6 )
		pygame.draw.line( bg.sf, self.color, p7, p8 )

class Crosshair():
	"""draws a targeting crosshair"""
	def __init__(self, size=25, color=(0,255,0)):
		self.color = color
		self.size = size
		self.x = 250
		self.y = 150

	def draw(self, bg):
		p1 = ( self.x, self.y - (self.size/2) )
		p2 = ( self.x, self.y + (self.size/2) )
		p3 = ( self.x - (self.size/2), self.y )
		p4 = ( self.x + (self.size/2), self.y )
		pygame.draw.line( bg.sf, self.color, p1, p2 )
		pygame.draw.line( bg.sf, self.color, p3, p4 )

	def delete(self, bg):
		prev = self.color
		self.color = bg.color
		self.draw(bg)
		self.color = prev

class Bargraph():
	"""draws a bar graph"""
	def __init__(self, bg, place, size=(20,250), color=(0,128,0)):
		self.bg = bg
		self.size = size
		self.place = place
		self.color = color

	def draw(self, fillfactor):
		# erase the whole area:
		pygame.draw.rect( bg.sf, bg.color, (self.place[0], self.place[1], self.size[0], self.size[1]), 0)
		# draw the border:
		pygame.draw.rect( bg.sf, self.color, (self.place[0], self.place[1], self.size[0], self.size[1]), 1)
		# draw the filling:
		pygame.draw.rect( bg.sf, self.color, (self.place[0], self.place[1]+(1-fillfactor)*self.size[1], self.size[0], fillfactor*self.size[1]), 0)

class Joystick():
	"""gets data from the joystick"""
	def __init__(self):
		if pygame.joystick.get_count():
			print "Initializing first joystick."
			self.dev = pygame.joystick.Joystick(0)
			self.dev.init()
			self.present = 1
		else:
			self.present = 0

	def getXY(self):
		return ( self.dev.get_axis(0), self.dev.get_axis(1) )

class Telemetry():
	"""gets data from the remote board."""
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.connected = 0
		self.fresh = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(3.0)
		self.i = sb2_input.inputData()
		self.o = sb2_output.outputData()
		self.a = 0
		self.t = time.time()
		self.blackout_histo = Histogram()
		thread.start_new_thread(self.receive, ())

	def receive(self):
		while True:
			try:
				self.sock.connect((self.host, self.port))
				self.connected = 1
				bytes_i = len(self.i.serialize())
				bytes_o = len(self.o.serialize())
				#print bytes_i, bytes_o
				while True:
					received = self.sock.recv(bytes_i + bytes_o)
					self.t_1 = self.t
					self.t = time.time()
					self.blackout_histo.inc(int(1000 * (self.t - self.t_1)))
					self.i.deserialize(received[0:bytes_i])
					self.o.deserialize(received[bytes_i:bytes_i+bytes_o])
					self.fresh = 1
			except:
				self.connected = 0
				self.sock.close()

	def getJoystick(self):
		return (self.i.jsX, self.i.jsY)

	def getTorque(self):
		return (self.o.l_trq, self.o.r_trq, self.i.motLC, self.i.motRC)
    
	def getTimes(self):
		self.fresh = 0
		return (self.o.t_in, self.o.t_proc, self.o.t_out, self.o.t_cycl)

	def getAccel(self):
		return (self.i.accX, self.i.accY)

	def getGps(self):
		return (self.i.gpsVld, self.i.gpsSpd, self.i.gpsHdng)


class Histogram():
	"""holds event frequency data."""
	def __init__(self):
		self.data = dict()

	def inc(self, key):
		if key not in self.data:
			self.data[key] = 1
		else:
			self.data[key] = self.data[key] + 1

	def getall(self):
		ks = self.data.keys()
		ks.sort(None, None, True)
		return ((k, self.data[k]) for k in ks)


# initialization routine:
pygame.init()
bg = Window()
frame = Sights()
cross = Crosshair()
left_torque_graph = Bargraph(bg, (bg.width/2 - frame.size/2 - 100, bg.height/2 - frame.size/2))
right_torque_graph = Bargraph(bg, (bg.width/2 + frame.size/2 + 75, bg.height/2 - frame.size/2))
clock = pygame.time.Clock()
stick = Joystick()
tele = Telemetry("192.168.5.202", 11000)
timer_histo = Histogram()
input_histo = Histogram()
proc_histo = Histogram()
output_histo = Histogram()
total_histo = Histogram()
histo_show = False

# event loop:
while True: 

    # collect input:
	events = pygame.event.get()
	if stick.present:
		X, Y = stick.getXY()
	else:
		X, Y = tele.getJoystick()
	fresh_data = tele.fresh
	(ti, tp, to, tc) = tele.getTimes()

    # process it:
	for event in events:
		if event.type == QUIT: 
			sys.exit(0) 
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE or event.unicode == 'q':
				sys.exit(0)
			if event.unicode == 'h':
				histo_show = not histo_show

	cross.x = bg.width/2 + ( frame.size/2 * X )
	cross.y = bg.height/2 + ( frame.size/2 * Y )

	if fresh_data:
		input_histo.inc("%0.1f" % (1000 * ti))
		proc_histo.inc("%0.1f" % (1000 * tp))
		output_histo.inc("%0.1f" % (1000 * to))
		timer_histo.inc("%0.1f" % (1000 * tc))
		total_histo.inc("%0.1f" % (1000 * (ti+tp+to)))

    # update screen:

	(hs, vs1) = bg.write("connected = %d" % tele.connected, 10, 10)

	if histo_show:

		(hs1, vs) = bg.write("blackout histogram:", 10, 10+vs1)
		for t in tele.blackout_histo.getall():
			(hs, vs) = bg.write("   %sms : %d" % (t[0], t[1]), 10, 5+vs)
	
		if tele.connected:

			(hs2, vs) = bg.write("loop timer histogram:", hs1+10, 10+vs1)
			for t in timer_histo.getall():
				(hs, vs) = bg.write("   %sms : %d" % (t[0], t[1]), hs1+10, 5+vs)

			(hs3, vs) = bg.write("input histogram:", hs2+10, 10+vs1)
			for t in input_histo.getall():
				(hs, vs) = bg.write("   %sms : %d" % (t[0], t[1]), hs2+10, 5+vs)

			(hs4, vs) = bg.write("processing histogram:", hs3+10, 10+vs1)
			for t in proc_histo.getall():
				(hs, vs) = bg.write("   %sms : %d" % (t[0], t[1]), hs3+10, 5+vs)

			(hs5, vs) = bg.write("output histogram:", hs4+10, 10+vs1)
			for t in output_histo.getall():
				(hs, vs) = bg.write("   %sms : %d" % (t[0], t[1]), hs4+10, 5+vs)

			(hs6, vs) = bg.write("total histogram:", hs5+10, 10+vs1)
			for t in total_histo.getall():
				(hs, vs) = bg.write("   %sms : %d" % (t[0], t[1]), hs5+10, 5+vs)

	bg.write("X=%0.2f Y=%0.2f" % (X, Y), cross.x+10, cross.y+10)

	bg.redraw()
	frame.draw(bg)
	cross.draw(bg)
	left_torque_graph.draw(0.5+tele.o.l_trq/2)
	right_torque_graph.draw(0.5+tele.o.r_trq/2)
	pygame.display.flip()

	# wait 1/x seconds
	if fresh_data:
		clock.tick(25)
	else:
		clock.tick(100)

# the end
