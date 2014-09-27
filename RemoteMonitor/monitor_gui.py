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
# the Trike controller via a network socket to monitor the internal
# state of the controller in real time. It requires PyGame.
#

import sys, os, pygame, time, getopt
sys.path.append("../SoapBox") # input & output are shared.
import gui_data, gui_widgets
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

bg = gui_widgets.Window()

horiz_divs = 10
vert_divs = 5

# centre widgets:
frame = gui_widgets.Sights(bg, 0.75*bg.width/horiz_divs)
cross = gui_widgets.Crosshair(bg)

# left widgets:
left_batt_bar = gui_widgets.Bargraph(bg, "Ubat [V]", (bg.width/horiz_divs -25, bg.height/vert_divs), (20, 30), (30, 2*bg.height/vert_divs), (0, 100, 0))
left_temp_bar = gui_widgets.Bargraph(bg, "T [C]", (2*bg.width/horiz_divs -25, bg.height/vert_divs), (10, 50), (25, 2*bg.height/vert_divs), (200, 0, 50))
left_torque_bar = gui_widgets.Bargraph(bg, "I [A]", (3*bg.width/horiz_divs -25, bg.height/vert_divs), (0, 25.5), (30, 2*bg.height/vert_divs), (0,0,200))
left_pwm_bar = gui_widgets.Bargraph(bg, "PWM", (4*bg.width/horiz_divs -25, bg.height/vert_divs), (-1, 1), (50, 2*bg.height/vert_divs))

# right widgets:
right_pwm_bar = gui_widgets.Bargraph(bg, "PWM", (6*bg.width/horiz_divs -25, bg.height/vert_divs), (-1,1), (50, 2*bg.height/vert_divs))
right_torque_bar = gui_widgets.Bargraph(bg, "I [A]", (7*bg.width/horiz_divs -25, bg.height/vert_divs), (0, 25.5), (30, 2*bg.height/vert_divs), (0,0,200))
right_temp_bar = gui_widgets.Bargraph(bg, "T [C]", (8*bg.width/horiz_divs -25, bg.height/vert_divs), (10, 50), (25, 2*bg.height/vert_divs), (200, 0, 50))
right_batt_bar = gui_widgets.Bargraph(bg, "Ubat [V]", (9*bg.width/horiz_divs -25, bg.height/vert_divs), (20, 30), (30, 2*bg.height/vert_divs), (0, 100, 0))

# bottom widgets:


# data objects:
if not testing:	log = gui_data.FileLog("datalog.csv")
clock = pygame.time.Clock()
stick = gui_data.Joystick()
timer_histo = gui_data.Histogram()
input_histo = gui_data.Histogram()
proc_histo = gui_data.Histogram()
output_histo = gui_data.Histogram()
total_histo = gui_data.Histogram()
histo_show = False
paused = False
remote_control = False
if testing:
	tele = gui_data.DummyTelemetry()
else:
	tele = gui_data.Telemetry("192.168.5.202", 11000)
	log.write(tele.i.logHeader() + tele.o.logHeader() + "\n")
screen_width = 1.0 * pygame.display.Info().current_w
screen_height = 1.0 * pygame.display.Info().current_h

# event loop:
while True: 

    # collect input:
	events = pygame.event.get()
	X, Y = tele.getJoystick()
	fresh_data = tele.fresh
	(ti, tp, to, tc) = tele.getTimes()

    # send data back
	if remote_control:
		rX = rY = 0.0
		if stick.present:
			rX, rY = stick.getXY()
		else:
			(b1, b2, b3) = pygame.mouse.get_pressed()
			if b3: # hold the right mouse button to make it the joystick.
				(rX, rY) = pygame.mouse.get_pos()
				rX = (rX / screen_width) * 2.0 - 1.0
				rY = (rY / screen_height) * 2.0 - 1.0
		tele.setJoystick(rX, rY)

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
				tele.setRemote(remote_control)

	cross.x = bg.width/2 + ( frame.size/2 * X )
	cross.y = bg.height/2 + ( frame.size/2 * Y )

	if fresh_data:
		input_histo.inc("%0.1f" % (1000 * ti))
		proc_histo.inc("%0.1f" % (1000 * tp))
		output_histo.inc("%0.1f" % (1000 * to))
		timer_histo.inc("%0.1f" % (1000 * tc))
		total_histo.inc("%0.1f" % (1000 * (ti+tp+to)))

	# dump all data to file in TEXT format.
	if not testing:	log.write(tele.i.log() + tele.o.log() + "\n")

	if paused:
		clock.tick(25)
		continue

    # update screen:

	(hs, vs) = bg.write("packet errors = %d; bandwidth = %0.1f kb/s" % (tele.glitches, tele.bw), 10, 10)
	(hs, vs1) = bg.write("i2c glitches: L=%d, R=%d" % (tele.o.glitches_l, tele.o.glitches_r), 10, vs+10)

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

		# LEFT
		if not tele.i.failed_l: # if able to read from bridge
			left_temp_bar.draw(tele.i.brgLT)
			left_torque_bar.draw(tele.i.motLC)
			left_batt_bar.draw(tele.i.batLV)
		if not tele.o.failed_l: # if able to write to bridge
			left_pwm_bar.draw(tele.o.l_trq)

		# CENTRE
		if remote_control or (not remote_control and not tele.i.failed_j):
			if not remote_control : frame.draw()
			cross.draw()

		# RIGHT
		if not tele.i.failed_r: # if able to read from bridge
			right_batt_bar.draw(tele.i.batRV)
			right_torque_bar.draw(tele.i.motRC)
			right_temp_bar.draw(tele.i.brgRT)
		if not tele.o.failed_r: # if able to write to bridge
			right_pwm_bar.draw(tele.o.r_trq)

	pygame.display.flip()

	# wait 1/x seconds
	clock.tick(25)

#	if testing:
#		paused = True

# the end
