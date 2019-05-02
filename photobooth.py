#!/usr/bin/python3

import datetime
import os
from time import sleep

import yaml

from photoutils import PushButton, LedButton, Camera
from logging import Logging

log = Logging()


class Photo:
    ''' A class that implements a photobooth on RaspberryPi with PushButton and PiCamera

    Attributes
    ------------
    config : dict
        dictionary with configuration, for description check "photoconfig.yaml"
            self.photopaths = []
        photopaths : list
            list of strings with paths of images captured in the current run
        ledbutton : LedButton
            instance of photoutils.LedButton class, handling the LED behaviour
        pressbutton : PushButton
            instance of photoutils.PushButton class, handling the detection od button presses
        camera : Camera
            instance of photoutils.Camera class, handles the needed camera display methods

    Methods:
    ------------
    wait_for_press(im1='', im2='')
        waits for button press with LED blinking and alternating images on display
    taking_photo(num=1, iffilter=False)
        sets the image target file name and captures the image
    prep_and_photo
        displays all the intro images, captures photos, sets camera preview transparent and waits for button press
    finishing
        sets camera preview opaque, displays the "thank you" images
    close:
        releases camera, push button and led
    main:
        loops prep_and_photo and finishing
    '''
    def __init__(self, config=None):
        log.append("starting")
        if not config:
            with open("photoconfig.yaml", 'r') as stream:
                config = yaml.full_load(stream)
        self.config = config
        realpath = os.path.dirname(os.path.realpath(__file__))
        for (key, val) in self.config['paths'].items():
            self.config['paths'][key] = os.path.join(realpath, val)
        log.append("Saving to " + self.config['paths']['photopath'])

        self.photopaths = []
        self.ledbutton = LedButton(buttonbcm=self.config['pin_arcade_led'])
        self.pressbutton = PushButton(buttonbcm=self.config['pin_camera_btn'],
                                      autopress=self.config['autopress'])
        self.camera = Camera(self.config['camera'])

    def wait_for_press(self, im1='', im2=''):
        ''' waits for button press with LED blinking and alternating images on display

        Paramters
        ------------
        im1 : str, optional
            path for image to be displayed on lower layer
        im2 : str, optional
            path for image to be displayed on upper layer
        '''

        ov1 = None
        ov2 = None
        if im1:
            ov1 = self.camera.overlay_image(im1, 0, 3)
        if im2:
            ov2 = self.camera.overlay_image(im2, 0, 4)
        self.pressbutton.detect_press()
        while not self.pressbutton.waspressed:
            if ov2:
                ov2.alpha = 255
            self.ledbutton.turn_on(1)
            if ov2:
                ov2.alpha = 0
            sleep(1)
        if ov1:
            self.camera.remove_overlay(ov1)
        if ov2:
            self.camera.remove_overlay(ov2)


    def taking_photo(self, num=1, iffilter=False):
        '''sets the image target file name and captures the image

        Parameters
        ------------
        num : int, optional
            consecutive number of photo to be taken
        iffilter : bool, optional
            whether to use one of the camera filters
        '''
        log.append("taking photo")
        timestamp = str(datetime.datetime.now()).split('.')[0].replace(' ', '_').replace(':', '-')
        filename = timestamp + "_" + str(num) + "of" + str(self.config['total_pics']) + ".jpg"
        filepath = os.path.join(self.config['paths']['photopath'], filename)
        self.photopaths.append(filepath)
        # prep delay
        grnum = 1 if num==1 else (3 if num ==  self.config['total_pics'] else 2)
        self.camera.overlay_image(self.config['paths']['getready'] + str(grnum) + ".png", self.config['prep_delay'])
        # photo
        self.camera.take_photo(filepath, iffilter)
        with open(self.config['paths']['piclist'], 'a') as addrfile:
            addrfile.write(filename + '\r\n')
        log.append("Photo saved: " + filepath)
        self.ledbutton.turn_off(0.2)

    def prep_and_photo(self):
        log.append("Press the button to take a photo")
        self.wait_for_press(im1=self.config['paths']['introimg1'], im2=self.config['paths']['introimg2'])
        log.append("pressed")
        self.ledbutton.turn_on()
        log.append("fraktal")
        self.camera.overlay_image(im=self.config['paths']['startup2'], duration=self.config['startup_delay'])
        log.append("starting")
        self.camera.overlay_image(im=self.config['paths']['startup1'], duration=self.config['startup_delay'])
        log.append("clearing tmp photo locations file")
        if os.path.exists(self.config['paths']['piclist']):
            os.rename(self.config['paths']['piclist'],
                      self.config['paths']['garbage'] + str(datetime.datetime.now()).split('.')[0])
        self.photopaths.clear()
        self.taking_photo(1)
        for photo_number in range(2, self.config['total_pics'] + 1):
            self.taking_photo(num=photo_number, iffilter=True)
        with open(self.config['paths']['piclist'], 'a') as addrfile:
            addrfile.write("\n".join(self.photopaths))
        log.append("email instructions")
        self.camera.overlay_image(self.config['paths']['email_image'], self.config['timeout_email'])
        log.append("full transparency to get email")
        self.camera.set_transparent()
        log.append("waits for press")
        self.wait_for_press()
        # after press, email is gathered and control goes to finishing

    def finishing(self):
        self.camera.set_opaque()
        self.ledbutton.turn_on()
        log.append("processing")
        self.camera.overlay_image(im=self.config['paths']['processingimg'], duration=self.config['startup_delay'])
        log.append("preview")
        self.camera.img_preview(self.photopaths)
        log.append("finish img")
        self.camera.overlay_image(self.config['paths']['finished_image'], self.config['finish_time'])
        log.append("All done!")

    def close(self):
        log.append("logfile closed")
        self.ledbutton.close()
        self.pressbutton.close()
        self.camera.close()

    def main(self):
        while True:
            print("prepare for photo")
            self.prep_and_photo()
            print("after taking photo")
            self.finishing()


if __name__ == "__main__":
    try:
        photo = Photo()
        print("main")
        photo.main()
        photo.close()
    except KeyboardInterrupt:
        log.append("keyboard interrupt")
    except Exception as exception:
        log.append("unexpected error: " + str(exception))
