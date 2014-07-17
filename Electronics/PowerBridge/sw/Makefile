#
# Power H-Bridge Controller
#
# Copyright (c) 2010-2014 Nuno João
# http://www.EmbeddedDreams.com
#
# This file is part of DiffTrike.
#
# DiffTrike is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DiffTrike is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DiffTrike. If not, see <http://www.gnu.org/licenses/>.
#
# Available targets:
#
#   - all: build software
#   - clean: delete all files created
#   - fuses: sets the fuses
#   - program: programs the board
#   - produce: builds, sets the fuses and programs
#

# CPU type and frequency (in HZ).
MCU_TARGET  = attiny26
F_CPU       = 4000000UL

# Main application name (name of .ELF, .HEX, .BIN, .LST, .MAP).
PRG = main

# Object files. Set the dependencies at the end of this Makefile.
OBJ = main.o i2c_slave.o


############################################################################

# Get the environment.
include Makefile.env

ACPFLAGS = \
	-mcu=$(MCU_TARGET) \
	-fcpu=$(F_CPU) \

OPTIMIZATIONS = \
	-O2 \

override CFLAGS = \
	-pipe -g \
	-I$(INCDIR) \
	$(OPTIMIZATIONS) \
	-Wall \
	-mmcu=$(MCU_TARGET) \
	-DF_CPU=$(F_CPU) \
	-Werror \
	-DI2C_REGISTER_FILE_SIZE=8 \
	-DUSE_DON_TWI=$(USE_DON_TWI) \
#	-DDEBUG \

ifneq ($(MANDEP),)
override CFLAGS += -DMANUF_VREF_CAL 
endif

override LDFLAGS = -Wl,-Map,$(PRG).map

#===========================================================================

.PHONY : all size produce program fuses lockbits build deploy clean

# Default action: build the software.
all: build

build: $(PRG).elf lst hex bin size


$(PRG).elf: $(OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

size:
	$(SIZER) $(PRG).elf

lst:  $(PRG).lst
hex:  $(PRG).hex
bin:  $(PRG).bin

%.lst: %.elf
	$(OBJDUMP) -h -S $< > $@

%.hex: %.elf
	$(OBJCOPY) -j .text -j .data -O ihex $< $@

%.bin: %.elf
	$(OBJCOPY) -j .text -j .data -O binary $< $@

#===========================================================================

# Build, set the fuses and burn the program in the uC.
produce: hex fuses program 

tproduce: produce

# Target to burn the program in the flash.
program:
	$(BURNER) -e
	$(BURNER) -bp $(PRG).hex

# Path to current directory, in components splitted by spaces format.
UNIXPWDPATH = $(shell pwd | cut -c3- | sed -e "s/\\\// /g")

# Deploy the project.
deploy:
	#@echo "### DEPLOY COMPLETED ###"

# Enable FLASH/EEPROM protection options (no read, no write).
lockbits:
	$(BURNER) -lw 0

# Set Tiny26 fuses for internal 4MHz RC clock (2MHz-e2, 4MHz-e3, 8MHz-e4),
# enable preserve EEPROM during chip erase (high fuse byte),
# enable BOD for 4V.
fuses:
	$(BURNER) -fw ffff f0e3
	$(BURNER) -fw ff e3

rfuses:
	$(BURNER) -fr


help:
	@echo "Available targets: build, produce, tproduce, fuses, program, lock, setResetAsGpio, deploy, clean"
	@echo "The MAN/DEP FW can be built by adding 'MANDEP=yes'. Needs 'make manual' clean when switching."
	@echo "DEVTOOLSDIR = $(DEVTOOLSDIR)"
	@echo "SCHIPSDKDIR = $(SCHIPSDKDIR)"
	@echo "MCU_TARGET = $(MCU_TARGET)"
	@echo "F_CPU = $(F_CPU)"
	@echo "PRG = $(PRG)"
	@echo "OBJ = $(OBJ)"
	@echo "CFLAGS = $(CFLAGS)"
	@echo "LDFLAGS = $(LDFLAGS)"

clean:
	$(MAKE) --directory=$(SCHIPSDKDIR)sw -f Makefile clean MCU_TARGET=$(MCU_TARGET) F_CPU=$(F_CPU)
	-$(RM) $(OBJ)
	-$(RM) $(PRG).elf
	-$(RM) $(PRG).lst
	-$(RM) $(PRG).bin
	-$(RM) $(PRG).hex
	-$(RM) $(PRG).map
	-$(RM) *.?_sym
	-$(RM) *.i.tmp
	-$(RM) *.i.i
	-$(RM) *.s
	-$(RM) *.bak

############################################################################
## Add here any dependencies you need.

main.o: Makefile i2c_slave.h main.c
i2c_slave.o: Makefile i2c_slave.h
