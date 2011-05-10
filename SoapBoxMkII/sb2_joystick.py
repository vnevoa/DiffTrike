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

import pygame
from pygame.joystick import *

class Joystick():
    """initializes and gets data from the joystick"""                                                    

    def __init__(self, joystick_num):
        init = pygame.joystick.get_init()
        count = pygame.joystick.get_count()
        self.buttons = 0
        if (count >= joystick_num):
            self.dev = pygame.joystick.Joystick(joystick_num)
            print 'Initializing Joystick' + str(joystick_num) + ': ' + self.dev.get_name()
            self.dev.init()
            self.buttons = self.dev.get_numbuttons()
            self.hats = self.dev.get_numhats()
            self.trackballs = self.dev.get_numballs()
            self.present = 1
        else:
            self.present = 0
     
    def getXY(self):
        return ( self.dev.get_axis(0), self.dev.get_axis(1) )

    def getButtons(self):                                                                                
        ret = (0)                                                                                        
        #ret =                                                                                           
        #self.dev.get_button(0), self.dev.get_button(1), self.dev.get_button(2), self.dev.get_button(3) )
        return ret    

