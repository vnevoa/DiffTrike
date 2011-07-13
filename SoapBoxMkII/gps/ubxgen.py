#!/usr/bin/python
#
# ubx packet generator
#
# v0.1
#
# Wilfried Klaebe <wk-openmoko@chaos.in-kiel.de>
#
# Usage:
#
# ubxgen.py 06 13 04 00 01 00 00 00 > packet.ubx
#
# prepends 0xb5 0x62 header,
# appends checksum,
# outputs binary packet to stdout
#
# you can send the packet to GPS chip like this:
#
# cat packet.ubx > /dev/ttySAC1

import sys
import binascii

cs0=0
cs1=0

sys.stdout.write("\xb5\x62")

for d in sys.argv[1:]:
  c = binascii.unhexlify(d)
  sys.stdout.write(c)
  cs0 += ord(c)
  cs0 &= 255
  cs1 += cs0
  cs1 &= 255

sys.stdout.write(chr(cs0)+chr(cs1))

