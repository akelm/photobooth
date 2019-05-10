#!/usr/bin/python3

import os
from time import sleep

import RPi.GPIO as gpio

from photologging import Logging

PIN = 27  # pin (BCM)

log = Logging()


class Counter:
    def __init__(self, pin):
        log.append("counter init")
        self.count = 0
        self.pin = pin
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(PIN, gpio.FALLING, callback=lambda x: self.callback(), bouncetime=500)

    def callback(self):
        sleep(0.1)
        if gpio.input(self.pin):
            log.append("false trigger")
            return
        self.count += 1

    def remove_callback(self):
        gpio.remove_event_detect(self.pin)


if __name__ == "__main__":

    cnt = Counter(PIN)

    while True:
        if cnt.count == 1:
            sleep(5)
        if cnt.count == 1:
            log.append("reboot")
            cnt.remove_callback()
            os.system("sudo reboot")
        if cnt.count > 1:
            log.append("shutdown")
            cnt.remove_callback()
            os.system("sudo shutdown -h now")
        sleep(1)
