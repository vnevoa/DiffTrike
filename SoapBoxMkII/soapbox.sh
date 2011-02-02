#! /bin/sh
set -e

# /etc/init.d/soapbox: start and stop the "SoapBoxMkII control" daemon

APP=/home/root/sb2.py
BT=/sys/class/rfkill/rfkill0/state
WI=/sys/class/rfkill/rfkill1/state
USBHOST=/sys/devices/platform/s3c2410-ohci/usb_mode

test -x $APP || exit 0

case "$1" in
  start)

	echo -n "Starting SoapBoxMkII control application... "

	# network interfaces are auto configured and pulled up by 'ifup'.

	# disable Bluetooth transmitter:
	echo 0 > $BT # bluetooth off

	# enable USB Host mode (unpowered):
	ifconfig usb0 down
	echo host > $USBHOST
	modprobe usbhid
	modprobe joydev

	# launch control application:
	export SDL_JOYSTICK_DEVICE=/dev/input/js2
	start-stop-daemon -S -x $APP > /dev/null &
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

