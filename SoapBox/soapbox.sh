#! /bin/sh
set -e

# /etc/init.d/soapbox: start and stop the MyOwnHybrid "SoapBox control" daemon

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
	echo -n "Starting SoapBox control application... "
	# network interfaces are auto configured and pulled up by 'ifup'.
	# launch control application:
	#export SDL_JOYSTICK_DEVICE=/dev/input/js2
	start-stop-daemon -N -10 -S -x $APP | grep -v SDL &
        echo "done."
	;;

  stop)
    echo "Stopping SoapBox control application."
	start-stop-daemon -K -x /usr/bin/python $APP
	;;

  restart)
    echo "Restarting SoapBox control application."
	start-stop-daemon -K -x /usr/bin/python $APP
	sleep 5
	start-stop-daemon -N -10 -S -x $APP | grep -v SDL &
	;;

  *)
	echo "Usage: /etc/init.d/soapbox {start|stop|restart}"
	exit 1
esac

exit 0
