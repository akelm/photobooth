#!/usr/bin/python3

import os
from time import sleep

import RPi.GPIO as gpio

from photologging import Logging

log = Logging()

class counter:
    def __init__(self):
        log.append("counter init")
        self.count = 0

    def inc(self):
        self.count += 1


PIN = 27  # pin (BCM) where

gpio.setmode(gpio.BCM)
gpio.setup(PIN, gpio.IN, pull_up_down=gpio.PUD_UP)
cnt = counter()
gpio.add_event_detect(PIN, gpio.FALLING, callback=lambda x: cnt.inc(), bouncetime=500)

while True:
    if cnt.count == 1:
        sleep(5)
    if cnt.count == 1:
        log.append("reboot")
        os.system("sudo reboot")
    if cnt.count > 1:
        log.append("shutdown")
        os.system("sudo shutdown -h now")
    sleep(1)