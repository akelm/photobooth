#!/usr/bin/python3

import os
from time import sleep
import yaml

import RPi.GPIO as gpio

from photologging import Logging



log = Logging()


class Counter:
    def __init__(self, pin):
        log.append("counter init")
        self.count = 0
        self.pin = pin
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(self.pin, gpio.FALLING, callback=lambda x: self.callback(), bouncetime=500)

    def callback(self):
        sleep(0.1)
        if gpio.input(self.pin):
            log.append("false trigger")
            return
        self.count += 1

    def remove_callback(self):
        gpio.remove_event_detect(self.pin)

class ShutdownReset:
    def __init__(self, config=None):
        if not config:
            with open("photoconfig.yaml", 'r') as stream:
                config = yaml.full_load(stream)
        #self.config = config
        self.cnt = Counter(config["pin_reset_btn"])

    def run(self):
        while True:
            if self.cnt.count == 1:
                sleep(5)
            if self.cnt.count == 1:
                log.append("reboot")
                self.cnt.remove_callback()
                os.system("reboot")
            if self.cnt.count > 1:
                log.append("shutdown")
                self.cnt.remove_callback()
                os.system("shutdown -h now")
            sleep(1)


if __name__ == "__main__":

    ShutdownReset().run()


