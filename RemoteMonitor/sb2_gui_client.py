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

class Window():
    """establishes the program window"""
    def __init__(self):
        self.width = 500
        self.height = 300
        self.color = (10, 10, 10)
        pygame.display.set_mode((self.width, self.height)) 
        pygame.display.set_caption('Joystick GUI')
        #pygame.mouse.set_visible(0)
        self.sf = pygame.display.get_surface()
        self.sf.fill(self.color)

    def redraw(self):
        self.sf.blit( self.sf, (0,0) )

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
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.X = self.Y = 0
		try:
			self.sock.connect((host, port))
			thread.start_new_thread(self.receive, ())
			self.present = 1
		except:
			self.present = 0
			self.X = self.Y = 0.5
			

	def receive(self):
		try:
			while 1:
				received = self.sock.recv(28)
				(self.t_in, self.t_proc, self.t_out, self.X, self.Y, self.right, self.left) = \
				struct.unpack('fffffff', received)
		except:
			self.X = self.Y = -0.5

	def getXY(self):
		return (self.X, self.Y)
    
def input(events): 
    for event in events: 
        if event.type == QUIT: 
            sys.exit(0) 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.unicode == 'q':
                sys.exit(0)
        #else: 
            #print event 


# initialization routine:
pygame.init()
bg = Window()
frame = Sights()
frame.draw(bg)
cross = Crosshair()
cross.draw(bg)
clock = pygame.time.Clock()
a = 0
stick = Joystick()
tele = Telemetry("192.168.5.202", 11000)

# event loop:
while True: 
    # wait 1/60 seconds
    clock.tick(60)

    # collect input:
    input(pygame.event.get())

    # delete mobile objects:
    cross.delete(bg)

    # process it:
    if stick.present:
        X, Y = stick.getXY()
    else:
	if tele.present:
		X, Y = tele.getXY()
	else:
	        a += 2*math.pi/360
	        a %= 2*math.pi
		X = math.cos(a)
		Y = math.sin(a)
    cross.x = bg.width/2 + ( frame.size/2 * X )
    cross.y = bg.height/2 + ( frame.size/2 * Y )

    # update screen:
    frame.draw(bg)
    cross.draw(bg)
    bg.redraw()
    pygame.display.flip()

