#!/usr/bin/python

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
sys.path.append("../SoapBox") # sb2_input & sb2_output are shared.
import sb2_gui_data, sb2_gui_widgets
from pygame.locals import * 
from pygame.gfxdraw import *

# parse command line arguments:
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

horiz_divs = 10
vert_divs = 5

# centre widgets:
frame = sb2_gui_widgets.Sights(bg, 0.75*bg.width/horiz_divs)
cross = sb2_gui_widgets.Crosshair(bg)
gps_radar = sb2_gui_widgets.Azimuth(bg, "GPS", (bg.width/2, 2 * bg.height/7), frame.size/2)

# left widgets:
left_batt_level = sb2_gui_widgets.Bargraph(bg, "Ubat [V]", (bg.width/horiz_divs -25, bg.height/vert_divs), (12, 36), (30, 2*bg.height/vert_divs), (0, 100, 0))
left_temp_graph = sb2_gui_widgets.Bargraph(bg, "T [C]", (2*bg.width/horiz_divs -25, bg.height/vert_divs), (10, 50), (25, 2*bg.height/vert_divs), (200, 0, 50))
left_torque_graph = sb2_gui_widgets.Bargraph(bg, "I [A]", (3*bg.width/horiz_divs -25, bg.height/vert_divs), (0, 20), (30, 2*bg.height/vert_divs), (0,0,200))
left_pwm_graph = sb2_gui_widgets.Bargraph(bg, "PWM", (4*bg.width/horiz_divs -25, bg.height/vert_divs), (-1, 1), (50, 2*bg.height/vert_divs))

# right widgets:
right_pwm_graph = sb2_gui_widgets.Bargraph(bg, "PWM", (6*bg.width/horiz_divs -25, bg.height/vert_divs), (-1,1), (50, 2*bg.height/vert_divs))
right_torque_graph = sb2_gui_widgets.Bargraph(bg, "I [A]", (7*bg.width/horiz_divs -25, bg.height/vert_divs), (0, 20), (30, 2*bg.height/vert_divs), (0,0,200))
right_temp_graph = sb2_gui_widgets.Bargraph(bg, "T [C]", (8*bg.width/horiz_divs -25, bg.height/vert_divs), (10, 50), (25, 2*bg.height/vert_divs), (200, 0, 50))
right_batt_level = sb2_gui_widgets.Bargraph(bg, "Ubat [V]", (9*bg.width/horiz_divs -25, bg.height/vert_divs), (12, 36), (30, 2*bg.height/vert_divs), (0, 100, 0))

# bottom widgets:
lateral_acc_graph = sb2_gui_widgets.Bargraph(bg, "Lat.Acc. [G]", (bg.width/2 - frame.size, 3.5*bg.height/vert_divs), (-2.5, 2.5), (frame.size*2, 50), (0,200,0))


# data objects:
log = sb2_gui_data.FileLog("datalog.csv")
clock = pygame.time.Clock()
stick = sb2_gui_data.Joystick()
timer_histo = sb2_gui_data.Histogram()
input_histo = sb2_gui_data.Histogram()
proc_histo = sb2_gui_data.Histogram()
output_histo = sb2_gui_data.Histogram()
total_histo = sb2_gui_data.Histogram()
histo_show = False
paused = False
remote_control = False
if testing:
	tele = sb2_gui_data.DummyTelemetry()
else:
	tele = sb2_gui_data.Telemetry("192.168.5.202", 11000)
log.write(tele.i.logHeader() + tele.o.logHeader() + "\n")
screen_width = 1.0 * pygame.display.Info().current_w
screen_height = 1.0 * pygame.display.Info().current_h

# event loop:
while True: 

    # collect input:
	events = pygame.event.get()
	if not remote_control:
		X, Y = tele.getJoystick()
	else:
		if stick.present:
			X, Y = stick.getXY()
		else:
			(b1, b2, b3) = pygame.mouse.get_pressed()
			if b3: # hold the right mouse button to make it the joystick.
				(X, Y) = pygame.mouse.get_pos()
				X = (X / screen_width) * 2.0 - 1.0
				Y = (Y / screen_height) * 2.0 - 1.0
			else:
				X = Y = 0.0
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
			if event.unicode == 'r':
				remote_control = not remote_control

	cross.x = bg.width/2 + ( frame.size/2 * X )
	cross.y = bg.height/2 + ( frame.size/2 * Y )

	if fresh_data:
		input_histo.inc("%0.1f" % (1000 * ti))
		proc_histo.inc("%0.1f" % (1000 * tp))
		output_histo.inc("%0.1f" % (1000 * to))
		timer_histo.inc("%0.1f" % (1000 * tc))
		total_histo.inc("%0.1f" % (1000 * (ti+tp+to)))

	# dump all data to file in TEXT format.
	log.write(tele.i.log() + tele.o.log() + "\n")

	if paused:
		clock.tick(25)
		continue

    # update screen:

	(hs, vs) = bg.write("packet errors = %d; bandwidth = %0.1f kb/s" % (tele.glitches, tele.bw), 10, 10)
	(hs, vs1) = bg.write("i2c glitches: right=%d, left=%d" % (tele.o.glitches_r, tele.o.glitches_l), 10, vs+10)

	if histo_show:  # show only histograms...

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

	else:	# show only widgets...
 
		bg.write("%0.2f %0.2f" % (X, Y), cross.x+10, cross.y+10)

	bg.redraw()

	if tele.connected and not histo_show:

		if not tele.o.failed_l:
			left_temp_graph.draw(tele.i.brgLT)
			left_torque_graph.draw(tele.i.motLC)
			left_batt_level.draw(tele.i.batLV)

		left_pwm_graph.draw(tele.o.l_trq)

		if remote_control or (not remote_control and not tele.i.failed_j):
			frame.draw()
			cross.draw()
		if tele.i.gpsVld:
			gps_radar.draw(tele.i.gpsHdng, tele.i.gpsSpd)
		lateral_acc_graph.draw(tele.i.accY)

		if not tele.o.failed_r:
			right_batt_level.draw(tele.i.batRV)
			right_torque_graph.draw(tele.i.motRC	)
			right_temp_graph.draw(tele.i.brgRT)

		right_pwm_graph.draw(tele.o.r_trq)

	pygame.display.flip()

	# wait 1/x seconds
	clock.tick(25)

#	if testing:
#		paused = True

# the end
