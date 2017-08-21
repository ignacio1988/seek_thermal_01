# You will need to have python 2.7 (3+ may work)
# and PyUSB 1.0
# and PIL 1.1.6 or better
# and numpy
# and scipy
# and ImageMagick

# Many thanks to the folks at eevblog, especially (in no particular order)
#   miguelvp, marshallh, mikeselectricstuff, sgstair and many others
#     for the inspiration to figure this out
# This is not a finished product and you can use it if you like. Don't be
# surprised if there are bugs as I am NOT a programmer..... ;>))


## https://github.com/sgstair/winusbdotnet/blob/master/UsbDevices/SeekThermal.cs

import Tkinter
import sys
import time

import numpy
import usb.core
import usb.util
from PIL import Image, ImageTk
from scipy.misc import toimage

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


def get_image():
    global im2arrF
    while True:
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
            calimg = Image.frombytes("I", (208, 156), ret9, "raw", "I;16")

            #  Convert the string array to an unsigned numpy int16 array
            im2arr = numpy.asarray(calimg)
            im2arrF = im2arr.astype('uint16')

        if status == 3:
            #  Convert the raw calibration data to a string array
            img = Image.frombytes("I", (208, 156), ret9, "raw", "I;16")

            #  Convert the string array to an unsigned numpy int16 array
            im1arr = numpy.asarray(img)
            im1arrF = im1arr.astype('uint16')

            #  Subtract the calibration array from the image array and add an offset
            additionF = (im1arrF - im2arrF) + 800

            #  convert to an image and display with imagemagick
            disp_img = toimage(additionF)
            # disp_img.show()

            return disp_img


root = Tkinter.Tk()
root.title('Seek Thermal camera')
root.bind("<Escape>", lambda e: root.quit())
# root.geometry('+%d+%d' % (208,156))

label_image = Tkinter.Label(root)
label_image.pack()

fps_t = 0
fps_f = 0


def show_frame(first=False):
    global fps_t, fps_f

    disp_img = get_image()
    if first: root.geometry('%dx%d' % (disp_img.size[0], disp_img.size[1]))
    tkpi = ImageTk.PhotoImage(disp_img)
    label_image.imgtk = tkpi
    label_image.configure(image=tkpi)
    label_image.place(x=0, y=0, width=disp_img.size[0], height=disp_img.size[1])

    now = int(time.time())
    fps_f += 1
    if fps_t == 0:
        fps_t = now
    elif fps_t < now:
        print '\rFPS: %.2f' % (1.0 * fps_f / (now - fps_t)),
        sys.stdout.flush()
        fps_t = now
        fps_f = 0

    label_image.after(1, show_frame)  # after 1ms, run show_frame again


show_frame(first=True)
root.mainloop()  # UI has control until user presses <<Escape>>
