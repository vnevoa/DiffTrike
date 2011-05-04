#! /bin/sh
set -e

# /etc/init.d/soapbox: start and stop the MyOwnHybrid "SoapBoxMkII control" daemon

APP=/home/root/sb2.py
BT=/sys/class/rfkill/rfkill0/state
WI=/sys/class/rfkill/rfkill1/state
USBHOST=/sys/devices/platform/s3c2410-ohci/usb_mode
ACC1=/sys/devices/platform/spi_s3c24xx_gpio.0/spi3.0
ACC2=/sys/devices/platform/spi_s3c24xx_gpio.0/spi3.1
GPS=/sys/devices/platform/gta02-pm-gps.0/power_on

test -x $APP || exit 0

case "$1" in
  start)

	echo -n "Starting SoapBoxMkII control application... "

	# network interfaces are auto configured and pulled up by 'ifup'.

	# disable Bluetooth transmitter:
	echo 0 > $BT

	# turn on GPS receiver:
	echo 1 > $GPS

	# enable USB Host mode:
	ifconfig usb0 down
	echo host > $USBHOST
	modprobe usbhid
	modprobe joydev

	# tune accelerometers:
	echo 50 > $ACC1/threshold
	echo 50 > $ACC2/threshold

	# launch control application:
	export SDL_JOYSTICK_DEVICE=/dev/input/js2
	start-stop-daemon -N -10 -S -x $APP > /dev/null &
        echo "done."

	;;
  stop)
        echo "Stopping SoapBoxMkII control application."
	start-stop-daemon -K -x /usr/bin/python $APP
	;;
  *)
	echo "Usage: /etc/init.d/soapbox {start|stop}"
	exit 1
esac

exit 0
