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
# This module implements the controller's joystick device driver.
# It depends on python-pygame.
#

import pygame, time
from pygame.joystick import *

class Joystick():
	"""initializes and gets data from the joystick"""                                                    

	def __init__(self, joystick_num):
		init = pygame.joystick.get_init()
		if not init: 
			print "Initializing Joystick module."
			pygame.joystick.init()
		count = pygame.joystick.get_count()
		self.buttons = 0
		if (count > joystick_num):
			self.dev = pygame.joystick.Joystick(joystick_num)
			print 'Initializing Joystick ' + str(joystick_num) + ': ' + self.dev.get_name()
			self.dev.init()
			self.buttons = self.dev.get_numbuttons()
			self.hats = self.dev.get_numhats()
			self.trackballs = self.dev.get_numballs()
			print "Joystick has "+ str(self.buttons) + " buttons, " + str(self.hats) + " hats, " + str(self.trackballs) + " trackballs."
			self.present = 1
		else:
			print "Joystick not found."
			self.present = 0

	def getXY(self):
		if self.present:
			return ( self.dev.get_axis(0), self.dev.get_axis(1) )
		else:
			return ( 0.0, 0.0 )

	def getButtons(self, highest = 1):
		ret = []
		for b in range(min(highest, self.buttons)):
			ret.append(self.dev.get_button(b))
		return ret    

# This is a simple test routine that only runs if this module is 
# called directly with "python sb_joystick.py"

if __name__ == '__main__':
    pygame.init();
    joy = Joystick(0);
    while True:
		t0 = time.time()
		pygame.event.pump()
		p = joy.getXY()
		b = joy.getButtons(4)
		t1 = time.time()
		print "X=%0.2f Y=%0.2f B0=%d B1=%d B2=%d B3=%d  T=%0.1f" % (p[0],p[1],b[0],b[1],b[2],b[3],(t1-t0)*1000)
		time.sleep(0.25)

