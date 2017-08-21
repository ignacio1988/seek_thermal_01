# coding:utf-8
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
import cv2
from numpy import random
import sys
import numpy
import usb.core
import usb.util
from PIL import Image as imge
from scipy.misc import toimage
import scipy.misc
import cv2
import os

# find our Seek Thermal device  289d:0010
dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)
if not dev: raise ValueError('Device not found')


def send_msg(bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
    assert (
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(data_or_wLength))


# alias method to make code easier to read
receive_msg = dev.ctrl_transfer


def deinit():
    '''Deinit the device'''
    msg = '\x00\x00'
    for i in range(3):
        send_msg(0x41, 0x3C, 0, 0, msg)


# set the active configuration. With no arguments, the first configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
ep = usb.util.find_descriptor(intf, custom_match=custom_match)  # match the first OUT endpoint
assert ep is not None

# Setup device
try:
    msg = '\x01'
    send_msg(0x41, 0x54, 0, 0, msg)
except Exception as e:
    deinit()
    msg = '\x01'
    send_msg(0x41, 0x54, 0, 0, msg)

# Some day we will figure out what all this init stuff is and
#  what the returned values mean.

send_msg(0x41, 0x3C, 0, 0, '\x00\x00')
ret1 = receive_msg(0xC1, 0x4E, 0, 0, 4)
# print ret1
ret2 = receive_msg(0xC1, 0x36, 0, 0, 12)
# print ret2

send_msg(0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')
ret3 = receive_msg(0xC1, 0x58, 0, 0, 0x40)
# print ret3

send_msg(0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')
ret4 = receive_msg(0xC1, 0x58, 0, 0, 0x40)
# print ret4

send_msg(0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')
ret5 = receive_msg(0xC1, 0x58, 0, 0, 0x18)
# print ret5

send_msg(0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')
ret6 = receive_msg(0xC1, 0x58, 0, 0, 0x0C)
# print ret6

send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
ret7 = receive_msg(0xC1, 0x3D, 0, 0, 2)
# print ret7

send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
send_msg(0x41, 0x3C, 0, 0, '\x01\x00')
ret8 = receive_msg(0xC1, 0x3D, 0, 0, 2)
# print ret8

im2arrF = None
i = 0
n = 0


class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 30)

    def stop(self):
        Clock.unschedule(self.update)

    def update(self, dt):
        global im2arrF

        # Send read frame request
        send_msg(0x41, 0x53, 0, 0, '\xC0\x7E\x00\x00')

        try:
            ret9 = dev.read(0x81, 0x3F60, 1000)
            ret9 += dev.read(0x81, 0x3F60, 1000)
            ret9 += dev.read(0x81, 0x3F60, 1000)
            ret9 += dev.read(0x81, 0x3F60, 1000)
        except usb.USBError as e:
            sys.exit()

        # Let's see what type of frame it is
        #  1 is a Normal frame, 3 is a Calibration frame
        #  6 may be a pre-calibration frame
        #  5, 10 other... who knows.
        status = ret9[20]
        # print ('%5d'*21 ) % tuple([ret9[x] for x in range(21)])

        if status == 1:
            #  Convert the raw calibration data to a string array
            calimg = imge.fromstring("I", (208, 156), ret9, "raw", "I;16")

            #  Convert the string array to an unsigned numpy int16 array
            im2arr = numpy.asarray(calimg)
            im2arrF = im2arr.astype('uint16')

        if status == 3:
            #  Convert the raw calibration data to a string array
            img = imge.fromstring("I", (208, 156), ret9, "raw", "I;16")

            #  Convert the string array to an unsigned numpy int16 array
            im1arr = numpy.asarray(img)
            im1arrF = im1arr.astype('uint16')

            #  Subtract the calibration array from the image array and add an offset
            additionF = (im1arrF - im2arrF) + 800

            #  convert to an image and display with imagemagick
            buf1 = toimage(additionF)
            # convert it to texture
            buf = buf1.tostring()
            image_texture = Texture.create(size=(additionF.shape[1], additionF.shape[0]), colorfmt='luminance')
            image_texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture
            return additionF

    def save_img(self):
        global i
        i += 1
        name_img = 'images/thermalseek_%d.jpeg' % (i,)
        img = self.update(0)
        scipy.misc.imsave(name_img, img)
        print img

    def save_raw(self):
        if not os.path.exists('../raw'):
            os.makedirs('../raw')
        global n
        n += 1
        name_raw = 'raw/therbamlseek_%d.npy' % (n,)
        img = self.update(0)
        numpy.save(name_raw, img)


class QrtestHome(BoxLayout):
    def init_qrtest(self):
        pass

    def dostart(self, *largs):
        self.ids.qrcam.start()

    def doexit(self):
        pass

    def save_img(self):
        pass


class thermalseekApp(App):
    def build(self):
        Window.clearcolor = (200, 0, 0, 1)
        # Window.size = (400, 300)
        homeWin = QrtestHome()
        # homeWin.init_qrtest()
        return homeWin


thermalseekApp().run()
