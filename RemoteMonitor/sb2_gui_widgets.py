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
# This implements several graphical widgets. It requires PyGame.
#

import pygame, math
from pygame.gfxdraw import *
from pygame.font import *
from pygame.locals import * 


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
		(h, v) = txt.sf.get_size()
		return (x + h, y + v)

	def redraw(self):
		self.sf.fill(self.color)
		while (len(self.txt)):
			txt = self.txt.pop()
			self.sf.blit(txt.sf, (txt.x, txt.y))

class Sights():
	"""draws the targeting sights"""
	def __init__(self, bg, size=250, color=(255,0,0)):
		self.bg = bg
		self.color = color
		self.size = size
		self.p1 = ( (bg.width - size)/2, (bg.height - size)/2 )
		self.p2 = ( (bg.width + size)/2, (bg.height - size)/2 )
		self.p3 = ( (bg.width - size)/2, (bg.height + size)/2 )
		self.p4 = ( (bg.width + size)/2, (bg.height + size)/2 )
		self.p5 = ( bg.width/2, -0.05*size + (bg.height - size)/2 )
		self.p6 = ( bg.width/2,  0.05*size + (bg.height + size)/2 )
		self.p7 = ( -0.05*size + (bg.width - size)/2, bg.height/2 )
		self.p8 = (  0.05*size + (bg.width + size)/2, bg.height/2 )

	def draw(self):
		# square
		pygame.draw.polygon( self.bg.sf, self.color, (self.p1, self.p2, self.p4, self.p3), 1)
		# cross
		pygame.draw.line( self.bg.sf, self.color, self.p5, self.p6 )
		pygame.draw.line( self.bg.sf, self.color, self.p7, self.p8 )


class Crosshair():
	"""draws a targeting crosshair"""

	def __init__(self, bg, size=25, color=(0,255,0)):
		self.bg = bg
		self.color = color
		self.size = size
		self.x = 250
		self.y = 150

	def draw(self):
		p1 = ( self.x, self.y - (self.size/2) )
		p2 = ( self.x, self.y + (self.size/2) )
		p3 = ( self.x - (self.size/2), self.y )
		p4 = ( self.x + (self.size/2), self.y )
		pygame.draw.line( self.bg.sf, self.color, p1, p2 )
		pygame.draw.line( self.bg.sf, self.color, p3, p4 )


class Bargraph():
	"""draws a bar graph"""

	def __init__(self, bg, place, lims=(-1,1), size=(50,250), color=(128,128,128)):
		self.bg = bg
		self.size = size
		self.place = place
		self.color = color
		self.lims = lims
		self.mult = lims[1] - lims[0]

	def draw(self, value):
		x = self.place[0]
		y = self.place[1]
		width =  self.size[0]
		height = self.size[1]
		# erase the whole area:
		pygame.draw.rect( self.bg.sf, self.bg.color, (x, y, width, height), 0)
		# write value text:
		txt = Text(format(value,"0.2f"), x, y)
		self.bg.sf.blit(txt.sf, (txt.x, txt.y))
		(h, v) = txt.sf.get_size()
		# draw the border:
		pygame.draw.rect( self.bg.sf, self.color, (x, y+v, width, height), 1)
		# draw the filling:
		fillfactor = (value - self.lims[0]) / self.mult
		if (height >= width):
			y = self.place[1]+(1-fillfactor)*self.size[1]
			height = fillfactor*self.size[1]
		else:
			x = self.place[0]+(1-fillfactor)*self.size[0]
			width = fillfactor*self.size[0]
		pygame.draw.rect( self.bg.sf, self.color, (x, y+v, width, height), 0)


class Azimuth():
	"""draws an azimuth circle"""

	def __init__(self, bg, place=(0,0), size=25, color=(0,255,0)):
		self.bg = bg
		self.centre = place
		self.color = color
		self.r = size

	def draw(self, deg, vel):
		# tell speed:
		txt = Text(format(vel,"0.2f"), self.centre[0], self.centre[1] - self.r - 20)
		self.bg.sf.blit(txt.sf, (txt.x, txt.y))
		# tell heading:
		pygame.draw.circle(self.bg.sf, self.color, self.centre, self.r, 1)
		rad = math.radians(deg)
		p = (self.centre[0] + self.r * math.sin(rad), self.centre[1] - self.r * math.cos(rad))
		pygame.draw.line(self.bg.sf, self.color, self.centre, p)


