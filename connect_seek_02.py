from PyQt4.QtGui import *
import numpy
import sys
import usb.core
import usb.util
from PIL import Image

im2arrF = None
additionF8 = None
additionF = None

class ConnectSeek:
    def __init__(self):

        #self.im2arrF = numpy.zeros((208, 156))
        self.buff_array8 = numpy.zeros((208, 156))
        self.fps_t = 0
        self.fps_f = 0
        # find our Seek Thermal device  289d:0010
        self.dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)
        if not self.dev:
            raise ValueError('Device not found')

        # alias method to make code easier to read
        self.receive_msg = self.dev.ctrl_transfer

        # set the active configuration. With no arguments, the first configuration will be the active one
        self.dev.set_configuration()

        # get an endpoint instance
        self.cfg = self.dev.get_active_configuration()
        self.intf = self.cfg[(0, 0)]

        self.additionF8 = numpy.zeros((208, 156))

        self.custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        self.ep = usb.util.find_descriptor(self.intf, custom_match=self.custom_match)  # match the first OUT endpoint
        assert self.ep is not None

    def send_msg(self, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        assert (self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(
            data_or_wLength))

    def deinit(self):
        '''Deinit the device'''
        msg = '\x00\x00'
        for i in range(3):
            self.send_msg(0x41, 0x3C, 0, 0, msg)

    def query(self):
        # Setup device
        try:
            msg = '\x01'
            self.send_msg(0x41, 0x54, 0, 0, msg)
        except Exception as e:
            self.deinit()
            msg = '\x01'
            self.send_msg(0x41, 0x54, 0, 0, msg)

        self.send_msg(0x41, 0x3C, 0, 0, '\x00\x00')
        self.ret1 = self.receive_msg(0xC1, 0x4E, 0, 0, 4)
        # print ret1
        self.ret2 = self.receive_msg(0xC1, 0x36, 0, 0, 12)
        # print ret2

        self.send_msg(0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')
        self.ret3 = self.receive_msg(0xC1, 0x58, 0, 0, 0x40)
        # print ret3

        self.send_msg(0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')
        self.ret4 = self.receive_msg(0xC1, 0x58, 0, 0, 0x40)
        # print ret4

        self.send_msg(0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')
        self.ret5 = self.receive_msg(0xC1, 0x58, 0, 0, 0x18)
        # print ret5

        self.send_msg(0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')
        self.ret6 = self.receive_msg(0xC1, 0x58, 0, 0, 0x0C)
        # print ret6

        self.send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
        self.ret7 = self.receive_msg(0xC1, 0x3D, 0, 0, 2)
        # print ret7

        self.send_msg(0x41, 0x3E, 0, 0, '\x08\x00')
        self.send_msg(0x41, 0x3C, 0, 0, '\x01\x00')
        self.ret8 = self.receive_msg(0xC1, 0x3D, 0, 0, 2)
        # print ret8

    def get_image(self):
        global im2arrF, additionF8, additionF

        # Send read frame request
        self.send_msg(0x41, 0x53, 0, 0, '\xC0\x7E\x00\x00')

        try:
            ret9 = self.dev.read(0x81, 0x3F60, 1000)
            ret9 += self.dev.read(0x81, 0x3F60, 1000)
            ret9 += self.dev.read(0x81, 0x3F60, 1000)
            ret9 += self.dev.read(0x81, 0x3F60, 1000)
        except usb.USBError as e:
            sys.exit()

        # Let's see what type of frame it is
        #  1 is a Calibration frame, 3 is a Normal frame
        #  6 may be a pre-calibration frame
        #  5, 10 other... who knows.
        status = ret9[20]

        if status == 1:
            #  Convert the raw calibration data to a byte array
            calimg = Image.frombytes("I", (208, 156), ret9, "raw", "I;16")

            #  Convert the string array to an unsigned numpy int16 array
            im2arr = numpy.asarray(calimg)
            im2arrF = im2arr.astype('int16')

        if status == 3:
            #  Convert the normal data to a byte array
            img = Image.frombytes("I", (208, 156), ret9, "raw", "I;16")

            #  Convert the string array to an unsigned numpy int16 array
            im1arr = numpy.asarray(img)
            im1arrF = im1arr.astype('int16')

            #  Subtract the calibration array from the image array and add an offset
            additionF = (im1arrF - im2arrF) + 800   # + 800
            #additionF8 = ((additionF - additionF.min()) / (additionF.ptp() / 255.0)).astype(numpy.uint8)

        return additionF


