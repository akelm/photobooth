#!/bin/bash
if ! pidof -x "sendphotos.py" > /dev/null; then
	 /home/pi/piknik2019/sendphotos.py > /dev/null 2>&1 &
fi
DISPLAY=:0.0 /home/pi/piknik2019/photoboothQt.py > /dev/null 2>&1 &