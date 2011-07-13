#!/usr/bin/python

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
# This script masks the "every second" interrupt of the Real
# Time Clock (RTC) in the PCF50633 (Power Management Unit) chip.
#

import i2c_lib

pmu = i2c_lib.I2CSlave('/dev/i2c-0', 0x73, True) # force usage, kernel is bound to it.
pmu.write(0x07, 0xC0)

