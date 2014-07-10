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
	def __init__(self, x, y, fcolor=(255,255,255), bcolor=(0,0,0)):
		self.x = x
		self.y = y
		self.bcolor = bcolor
		self.fcolor = fcolor
		self.font = pygame.font.SysFont("", 24)
	def write(self, txt):
		self.sf = self.font.render(txt, 0, self.fcolor, self.bcolor)

class Window():
	"""main window behaviour"""
	def __init__(self, fillcolor=(0, 0, 0)):
		self.color = fillcolor
		pygame.display.set_mode((0,0), 0) #pygame.FULLSCREEN)
		pygame.display.set_caption('SoapBox Mark II Control GUI')
		pygame.mouse.set_visible(0)
		self.sf = pygame.display.get_surface()
		self.width, self.height = self.sf.get_size()
		self.sf.fill(self.color)
		self.txt = []

	def write(self, text, x, y):
		txt = Text(x, y)
		txt.write(text)
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

	def __init__(self, bg, name, place, lims=(-1,1), size=(50,250), color=(128,128,128)):
		self.bg = bg
		self.x = place[0]
		self.y = place[1]
		self.w = size[0]
		self.h = size[1]
		self.name = Text(self.x, self.y + self.h - 10)
		self.name.write(name)
		self.value = Text(self.x, self.y)
		self.value.write("0.00")
		self.color = color
		self.lims = lims
		self.mult = 1.0 * lims[1] - lims[0] # making sure it is float.

	def draw(self, value = 0.0):
		# "erase" the whole area:
		pygame.draw.rect( self.bg.sf, self.bg.color, (self.x, self.y, self.w, self.h), 0)
		# draw name text at bottom:
		self.bg.sf.blit(self.name.sf, (self.name.x, self.name.y))
		# draw the border in between texts:
		(self.name_w, self.name_h) = self.name.sf.get_size()
		(self.value_w, self.value_h) = self.value.sf.get_size()
		pygame.draw.rect(self.bg.sf, self.color, (self.x, self.y + self.value_h, self.w, self.h - self.name_h - self.value_h), 1)
		# draw the filling inside the border and the value at the top:
		self.update(value)

	def update(self, value):

		# process value text at top:
		if (value < self.lims[0]):
			value = self.lims[0]
			self.value.write("<" + format(value,"0.2f"))
		elif (value > self.lims[1]):
			value = self.lims[1]
			self.value.write(">" + format(value,"0.2f"))
		else:
			self.value.write(format(value,"0.2f"))
		# draw it:
		self.bg.sf.blit(self.value.sf, (self.value.x, self.value.y))
		(self.value_w, self.value_h) = self.value.sf.get_size()

		# process the bar inside the border:
		fillfactor = (value - self.lims[0]) / self.mult
		x = self.x
		if (self.h >= self.w): # vertical bar
			y = self.y + self.value_h + (1.0 - fillfactor) * (self.h - self.name_h - self.value_h)
			w = self.w
			h = fillfactor * (self.h - self.name_h - self.value_h)
		else:                 # horizontal bar
			y = self.y + self.value_h
			w = fillfactor * self.w
			h = self.h - self.name_h - self.value_h
		# draw the filled part:
		pygame.draw.rect(self.bg.sf, self.color, (x, y, w, h), 0)

		# "erase" the rest:
		if (self.h >= self.w): # vertical bar
			y = self.y + self.value_h
			w = self.w
			h = (1.0 - fillfactor) * (self.h - self.name_h - self.value_h)
		else:                 # horizontal bar
			x = self.x + fillfactor * self.w
			y = self.y + self.value_h
			w = (1.0 - fillfactor) * self.w
			h = self.h - self.name_h - self.value_h
		pygame.draw.rect(self.bg.sf, (10,10,10), (x, y, w, h), 0)

class Azimuth():
	"""draws an azimuth circle"""

	def __init__(self, bg, name, place=(0,0), size=25, color=(0,255,0)):
		self.bg = bg
		self.centre = place
		self.color = color
		self.r = size
		self.name = Text(name, place[0]-size, place[1]+size-10)

	def draw(self, deg, vel):
		# tell speed:
		txt = Text(format(vel,"0.2f"), self.centre[0], self.centre[1] - self.r - 20)
		self.bg.sf.blit(txt.sf, (txt.x, txt.y))
		# tell heading:
		pygame.draw.circle(self.bg.sf, self.color, self.centre, int(self.r), 1)
		rad = math.radians(deg)
		p = (self.centre[0] + self.r * math.sin(rad), self.centre[1] - self.r * math.cos(rad))
		pygame.draw.line(self.bg.sf, self.color, self.centre, p)
		# show name:
		self.bg.sf.blit(self.name.sf, (self.name.x, self.name.y))


