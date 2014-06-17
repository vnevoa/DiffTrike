#! /bin/sh
set -e

# /etc/init.d/soapbox: start and stop the MyOwnHybrid "SoapBoxMkIV control" daemon

APP=/home/pi/SoapBox/sb.py
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

	echo -n "Starting SoapBoxMkIV control application... "

	# network interfaces are auto configured and pulled up by 'ifup'.

	# launch control application:
	start-stop-daemon -N -10 -S -x $APP | grep -v SDL &
        echo "done."

	;;
  stop)
        echo "Stopping SoapBoxMkIV control application."
	start-stop-daemon -K -x /usr/bin/python $APP
	;;
  *)
	echo "Usage: /etc/init.d/soapbox {start|stop}"
	exit 1
esac

exit 0
