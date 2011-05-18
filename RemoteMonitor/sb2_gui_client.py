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
# This implements a graphical application that connects to
# the Trike controller via a socket to monitor the internal
# state of the controller in real time. It requires PyGame.
#

import sys, os, pygame, time, getopt
sys.path.append("../SoapBoxMkII") # sb2_input & sb2_output are shared.
import sb2_gui_data, sb2_gui_widgets
from pygame.locals import * 
from pygame.gfxdraw import *

# parse commannd line arguments:
testing = False
try:
	opts, args = getopt.getopt(sys.argv[1:], "t")
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	sys.exit(2)
for o, a in opts:
	if (o == "-t"):
		testing = True

# do initializations:
pygame.init()
bg = sb2_gui_widgets.Window()
frame = sb2_gui_widgets.Sights()
cross = sb2_gui_widgets.Crosshair()
left_pwm_graph = sb2_gui_widgets.Bargraph(bg, (bg.width/2 - frame.size/2 - 100, bg.height/2 - frame.size/2))
right_pwm_graph = sb2_gui_widgets.Bargraph(bg, (bg.width/2 + frame.size/2 + 50, bg.height/2 - frame.size/2))
left_torque_graph = sb2_gui_widgets.Bargraph(bg, (bg.width/2 - frame.size/2 - 200, bg.height/2 - frame.size/2), (50, 250), (0,0,200))
right_torque_graph = sb2_gui_widgets.Bargraph(bg, (bg.width/2 + frame.size/2 + 150, bg.height/2 - frame.size/2), (50, 250), (0,0,200))
lateral_acc_graph = sb2_gui_widgets.Bargraph(bg, (bg.width/2 - 125, bg.height/2 + frame.size/2 + 50), (250, 50), (128,0,0))
clock = pygame.time.Clock()
stick = sb2_gui_data.Joystick()
timer_histo = sb2_gui_data.Histogram()
input_histo = sb2_gui_data.Histogram()
proc_histo = sb2_gui_data.Histogram()
output_histo = sb2_gui_data.Histogram()
total_histo = sb2_gui_data.Histogram()
histo_show = False
paused = False
if testing:
	tele = sb2_gui_data.DummyTelemetry()
else:
	tele = sb2_gui_data.Telemetry("192.168.5.202", 11000)

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
			if event.unicode == 'p':
				paused = not paused

	cross.x = bg.width/2 + ( frame.size/2 * X )
	cross.y = bg.height/2 + ( frame.size/2 * Y )

	if fresh_data:
		input_histo.inc("%0.1f" % (1000 * ti))
		proc_histo.inc("%0.1f" % (1000 * tp))
		output_histo.inc("%0.1f" % (1000 * to))
		timer_histo.inc("%0.1f" % (1000 * tc))
		total_histo.inc("%0.1f" % (1000 * (ti+tp+to)))

	if paused:
		clock.tick(25)
		continue

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

	bg.write("%0.2f %0.2f" % (X, Y), cross.x+10, cross.y+10)

	bg.redraw()
	frame.draw(bg)
	cross.draw(bg)
	left_pwm_graph.draw(0.5+tele.o.l_trq/2)
	right_pwm_graph.draw(0.5+tele.o.r_trq/2)
	left_torque_graph.draw(0.5+tele.i.motRC/40)
	right_torque_graph.draw(0.5+tele.i.motRC/40)
	lateral_acc_graph.draw(0.5+tele.i.accY/4)
	pygame.display.flip()

	# wait 1/x seconds
	if fresh_data:
		clock.tick(25)
	else:
		clock.tick(100)

# the end
