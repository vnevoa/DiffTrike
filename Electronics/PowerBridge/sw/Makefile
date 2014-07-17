#
# H-Bridge controller
#
# Copyright (c) 2011 EmbeddedDreams
# http://www.EmbeddedDreams.com
#
# $Id: $
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

# Add TSLIB options here, if any.
TSLIB_OPTIONS =


############################################################################

ifeq ($(SCHIPSDKDIR),)
$(error Missing environment variable SCHIPSDKDIR pointing to SDK installation.)
endif

# Get the environment.
include $(SCHIPSDKDIR)sw/Makefile.env

ACPFLAGS = \
	-mcu=$(MCU_TARGET) \
	-fcpu=$(F_CPU) \

OPTIMIZATIONS = \
	-O2 \

override CFLAGS = \
	-DI2C_REGISTER_FILE_SIZE=8 \
	-pipe -g \
	$(TSLIB_OPTIONS) \
	-I$(INCDIR) \
	$(OPTIMIZATIONS) \
	-Wall \
	-mmcu=$(MCU_TARGET) \
	-DF_CPU=$(F_CPU) \
	-Werror \
	-DUSE_DON_TWI=$(USE_DON_TWI) \
#	-DDEBUG \

ifneq ($(MANDEP),)
override CFLAGS += -DMANUF_VREF_CAL 
endif

override LDFLAGS = -Wl,-Map,$(PRG).map

#===========================================================================

.PHONY : all size produce program fuses lockbits build deploy clean $(SCHIPSDKDIR)sw/tslib.a

# Default action: build the software.
all: build

build: $(PRG).elf lst hex bin size


$(PRG).elf: $(OBJ) $(SCHIPSDKDIR)sw/tslib.a
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

# Eliminate the implicit compilation rule, so that we can
# "override" the normal pipeline with a different build sequence.
%.o: %.c

# Preprocess a C file, then pass it through the AVR-C Preprocessor.
%.i: %.c
	$(CC) $(CFLAGS) -E -o $@.tmp $<
	$(AVRCPP) $(ACPFLAGS) -in=$@.tmp -out=$@
	$(RM) $@.tmp

# After AVRCPP, proceed with the compilation.
%.o: %.i
	$(CC) $(CFLAGS) -c -o $@ $<

# Rule to build TSLib.
$(SCHIPSDKDIR)sw/tslib.a:
	$(MAKE) --directory=$(SCHIPSDKDIR)sw \
		MCU_TARGET=$(MCU_TARGET) F_CPU=$(F_CPU) TSLIB_OPTIONS=$(TSLIB_OPTIONS)

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
	#sed -e "s/@@DEVDIR@@/[file join \\/$(UNIXPWDPATH)]/g" < ED1021_GUI.tcl > ED1021Gui.tcl
	#$(TCLTKFREEWRAP) ED1021Gui.tcl -f extraFilesToWrap.txt -i ED1021Gui.ico -o ED1021Gui.exe
	#$(GZIP) -c -9 ED1021Gui.exe > ED1021Gui.gz
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
	@echo "TSLIB_OPTIONS = $(TSLIB_OPTIONS)"
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
	-$(RM) ED1021Gui.tcl ED1021Gui.gz ED1021Gui.exe

############################################################################
## Add here any dependencies you need.

main.o: Makefile i2c_slave.h main.c
i2c_slave.o: Makefile i2c_slave.h
