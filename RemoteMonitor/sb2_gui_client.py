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

import sys, os, math, pygame, thread, socket, struct
from pygame.locals import * 
from pygame.gfxdraw import *
from pygame.joystick import *
from pygame.font import *

class Text():
	def __init__(self, txt, x, y):
		self.font = pygame.font.SysFont("", 24)
		self.sf = self.font.render(txt, 0, (255,255,255), (0,0,0))
		self.x = x
		self.y = y

class Window():
	"""establishes the program window"""
	def __init__(self):
		self.color = (10, 10, 10)
		pygame.display.set_mode((0,0), pygame.FULLSCREEN) 
		pygame.display.set_caption('SoapBox Mark II Control GUI')
		pygame.mouse.set_visible(0)
		self.sf = pygame.display.get_surface()
		self.width, self.height = self.sf.get_size()
		self.sf.fill(self.color)
		self.txt = []

	def write(self, text, x, y):
		txt = Text(text, x, y)
		self.txt.append(txt)
		return txt.sf.get_size()

	def redraw(self):
		self.sf.fill(self.color)
		while (len(self.txt)):
			txt = self.txt.pop()
			self.sf.blit(txt.sf, (txt.x, txt.y))

class Sights():
	"""draws the targeting sights"""
	def __init__(self):
		self.color = (255,0,0)
		self.size = 250

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
	"""draws the targeting crosshair"""
	def __init__(self):
		self.color = (0,255,0)
		self.size = 25
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
		self.a = 0
		self.t_in = self.t_proc = self.t_out = 0
		self.X = self.Y = 0
		self.right = self.left = 0
		thread.start_new_thread(self.receive, ())

	def receive(self):
		while True:
			try:
				self.sock.connect((self.host, self.port))
				self.connected = 1
				while True:
					received = self.sock.recv(28)
					(self.t_in, self.t_proc, self.t_out, self.X, self.Y, self.right, self.left) = struct.unpack('fffffff', received)
					self.fresh = 1
			except:
				self.connected = 0

	def getXY(self):
		if not self.connected:
			self.a += 2*math.pi/360
			self.a %= 2*math.pi
			self.X = math.cos(self.a)
			self.Y = math.sin(self.a)
		return (self.X, self.Y)

	def getTimes(self):
		if not self.connected:
			self.t_in = abs(self.X) * 1000
			self.t_out = abs(self.Y) * 1000
			self.t_proc = abs(self.X * self.Y) * 1000
		return (self.t_in, self.t_proc, self.t_out)

	def getWheels(self):
		if not self.connected:
			self.right = self.X * 100
			self.left = self.Y * 100
		return (self.right, self.left)
    

# initialization routine:
pygame.init()
bg = Window()
frame = Sights()
cross = Crosshair()
clock = pygame.time.Clock()
stick = Joystick()
tele = Telemetry("192.168.5.202", 11000)

# event loop:
while True: 

    # wait 1/x seconds
	clock.tick(20)

    # collect input:
	events = pygame.event.get()
	if stick.present:
		X, Y = stick.getXY()
	else:
		X, Y = tele.getXY()
	(ti, tp, to) = tele.getTimes()

    # process it:
	for event in events: 
		if event.type == QUIT: 
			sys.exit(0) 
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE or event.unicode == 'q':
				sys.exit(0)
	cross.x = bg.width/2 + ( frame.size/2 * X )
	cross.y = bg.height/2 + ( frame.size/2 * Y )

    # update screen:
	(hs, vs) = bg.write("connected = %d, fresh = %d" % (tele.connected, tele.fresh), 10, 10)
	if tele.fresh:
		bg.write("X=%0.3f Y=%0.3f" % (X, Y), cross.x+10, cross.y+10)
		bg.write("input = %0.1f ms" % (1000*ti), 10, 10+vs)
		bg.write("proc = %0.1f ms" % (1000*tp), 10, 10+vs*2)
		bg.write("output = %0.1f ms" % (1000*to), 10, 10+vs*3)
		bg.write("total = %0.1f ms" % (1000*(ti+tp+to)), 10, 10+vs*4)
	tele.fresh = 0
	bg.redraw()
	frame.draw(bg)
	cross.draw(bg)
	pygame.display.flip()

# the end
