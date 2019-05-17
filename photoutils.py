from time import sleep

import picamera
import RPi.GPIO as gpio
from PIL import Image

from photologging import Logging

log = Logging()


class PushButton:
    ''' A class handling the response from push button connected to GPIO in RaspberryPi

    Attributes
    ------------
    buttonbcm : int
        number of GPIO pin to which button is connected in BCM numbering
    autopress : bool
        whether the button should be pressed automatically (for testing)
    waspressed : bool
        flag to use outside class indicating whether button has been pressed

    Methods
    ------------
    detect_press()
        starts event from RPi.GPIO library that monitors for press and assigns set_press as event callback
    set_pressed()
        sets waspressed flag, removes event detection RPi.GPIO library for the button
    close()
        triggers set_pressed() and releases the GPIO slot assignment
    '''

    def __init__(self, buttonbcm=17, autopress=False):
        self.buttonbcm = buttonbcm
        self.autopress = autopress
        self.waspressed = False
        gpio.setmode(gpio.BCM)
        gpio.setup(self.buttonbcm, gpio.IN, pull_up_down=gpio.PUD_UP)

    def detect_press(self):
        if self.autopress:
            self.waspressed = True
        else:
            self.waspressed = False
            gpio.add_event_detect(self.buttonbcm, gpio.FALLING,
                                  callback=lambda x: self.set_pressed(), bouncetime=300)
            log.append("waits for press")

    def set_pressed(self):
        sleep(0.1)
        if gpio.input(self.buttonbcm):
            log.append("false trigger")
            return
        self.waspressed = True
        log.append("button pressed")
        gpio.remove_event_detect(self.buttonbcm)

    def close(self):
        self.set_pressed()
        gpio.cleanup(self.buttonbcm)


class LedButton:
    ''' A class handling the behaviour of LED (possibly inside the button) connected to GPIO in RaspberryPi

    Attributes
    ------------
    buttonbcm : int
        number of GPIO pin to which button is connected in BCM numbering

    Methods
    ------------
    single_blink(halfperiod=0.5)
        performs single blink (on for halfperiod seconds, and off for halfperiod seconds)
    turn_on(time=0.0)
        turns LED on; if time (in seconds) > 0, turns LED off after that time
    turn_off(time=0.0)
        turns LED off; if time (in seconds) > 0, turns LED on after that time
    close()
        turn LED off and releases the GPIO slot assignment
    '''

    def __init__(self, buttonbcm=4):
        self.buttonbcm = buttonbcm
        gpio.setmode(gpio.BCM)
        gpio.setup(self.buttonbcm, gpio.OUT, initial=gpio.LOW)

    def single_blink(self, halfperiod=0.5):
        self.turn_on(time=halfperiod)
        sleep(halfperiod)

    def turn_on(self, time=0.0):
        gpio.output(self.buttonbcm, 1)
        if time:
            sleep(time)
            self.turn_off()

    def turn_off(self, time=0.0):
        gpio.output(self.buttonbcm, 0)
        if time:
            sleep(time)
            self.turn_on()

    def close(self):
        self.turn_off()
        gpio.cleanup(self.buttonbcm)


class Camera:
    ''' A class handling the PiCamera Display for the Photobooth

    Attributes
    ------------
    config : dict
        config file for camera and function paramters
    currfilter : int
        number of camera filter (from config) recently used
    filterlen : int
        length of list with camera filters
    camera.rotation : int
        rotation of camera preview
    camera.annotate_text_size : int
        text size for camera annotations
    camera.resolution : (int,int)
        resolution of the camera preview

    Methods
    ------------
    set_transparent()
        sets the camera preview (layer 2) transparent
    set_opaque()
        sets the camera preview (layer 2) opaque
    overlay_image(im, duration=0, layer=3)
        adds overlay from image above the camera preview
    remove_overlay(overlay_id=None)
        removes overlay from camera display
    take_photo(target='', iffilter=False)
        displays camera preview with preparation countdown, takes a single photo and writes it to file
    img_preview(imglist=None)
        displays preview of the captured photos
    close()
        stops camera preview
    '''

    def __init__(self, config):
        log.append("camera start")
        self.config = config
        self.currfilter = -1
        self.filterlen = len(self.config['filters'])
        picamera.PiCamera.CAPTURE_TIMEOUT = 60  # seconds
        try:
            self.camera = picamera.PiCamera()
        except Exception as e:
            log.append("error initializing the camera - exiting")
            log.append(" ".join(str(e).splitlines()))
            raise SystemExit
        self.camera.rotation = 0
        self.camera.annotate_text_size = 80
        self.camera.resolution = self.config['photo_wh']
        self.camera.start_preview(resolution=self.config['screen_wh'])

    def set_transparent(self):
        self.camera.preview.alpha = 0

    def set_opaque(self):
        self.camera.preview.alpha = 255

    def overlay_image(self, im, duration=0, layer=3):
        '''adds overlay from image above the camera preview

        Parameters
        -----------
        im : str
            path to image file
        duration : int, optional
            time in second after which overlay is removed
        layer : int, optional
            number of layer for overlay placement
        Returns
        picamera.PiOverlayRenderer
            a picamera.PiOverlayRenderer instance for created overlay
        '''

        if not im:
            return None
        img = Image.open(im)
        # Create an image padded to the required size with
        # mode 'RGB'
        pad = Image.new('RGB', (
            ((img.size[0] + 31) // 32) * 32,
            ((img.size[1] + 15) // 16) * 16,
        ))
        # Paste the original image into the padded one
        pad.paste(img, (0, 0))
        # Add the overlay with the padded image as the source,
        # but the original image's dimensions
        try:
            o_id = self.camera.add_overlay(pad.tobytes(), size=img.size)
        except AttributeError:
            o_id = self.camera.add_overlay(pad.tostring(), size=img.size)
        o_id.layer = layer
        if duration > 0:
            sleep(duration)
            self.camera.remove_overlay(o_id)
            return None
        else:
            return o_id

    def remove_overlay(self, overlay_id=None):
        if overlay_id:
            self.camera.remove_overlay(overlay_id)

    def take_photo(self, target='', iffilter=False):
        '''displays camera preview with preparation countdown, takes a single photo and writes it to file

        Parameters
        ------------
        target : str
            address to store the photo
        iffilter : bool, optional
            whether to apply one of the camera filters
        '''

        if not target:
            return
        log.append("filter " + str(iffilter))
        if iffilter:
            self.currfilter += 1
            if self.currfilter >= self.filterlen:
                self.currfilter -= self.filterlen
            log.append("filter " + self.config['filters'][self.currfilter])
            self.camera.image_effect = self.config['filters'][self.currfilter]
        for i in range(self.config['photo_countdown_time'], 0, -1):
            self.camera.annotate_text = "             ..." + str(i)
            sleep(1)
        self.camera.annotate_text = ""
        self.camera.capture(target)
        self.camera.image_effect = 'none'

    def img_preview(self, imglist=None, ov=False):
        '''displays preview of the captured photos

        Parameters
        ------------
        imglist : list
            list of strings with images locations
        '''

        if not self.config['noprev']:
            ov_list = []
            i = 0
            for photo in imglist:
                this_overlay = self.overlay_image(photo, 0, 3 + i)
                ov_list.append(this_overlay)
                i += 1
                sleep(self.config['photo_playback_time'])
            for ov in ov_list:
                self.remove_overlay(ov)

    def close(self):
        self.camera.stop_preview()
