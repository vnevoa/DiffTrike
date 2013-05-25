#! /bin/sh
set -e

# /etc/init.d/soapbox: start and stop the MyOwnHybrid "SoapBoxMkII control" daemon

APP=/home/pi/SoapBoxMkII-pi/sb2.py
WI=
USBHOST=
USBPOWER=
ACC1=
ACC2=
GPS=
LCD=/dev/tty0

test -x $APP || exit 0

case "$1" in
  start)

	echo -n "Starting SoapBoxMkII control application... "

	# network interfaces are auto configured and pulled up by 'ifup'.

	# launch control application:
	#export SDL_JOYSTICK_DEVICE=/dev/input/js2
	start-stop-daemon -N -10 -S -x $APP | grep -v SDL &
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
