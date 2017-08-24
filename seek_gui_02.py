from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import *
import scipy.misc
import time
import matplotlib.pyplot as plt
from connect_seek_02 import *
import sys
import numpy
import os

cam_connect = ConnectSeek()
cam_connect.query()
form_class = uic.loadUiType("cam.ui")[0]

i = 0
fps_t = 0
fps_f = 0
bad_pixels = []


class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.status = True

        self.pushButton.setCheckable(True)
        self.pushButton.clicked[bool].connect(self.RecStop)

        self.buff_qimg = QImage(numpy.zeros((208, 156)), 208, 156,
                                QtGui.QImage.Format_Indexed8)  # Declara Qimage Buffer
        self.buff_array = numpy.zeros((208, 256))
        self.additionF16 = numpy.zeros((208, 156))


    def Adq(self):
        seek_img16 = cam_connect.get_image()
        if seek_img16 is not None:
            if self.CorrectPatternHexa.isChecked():
                seek_img16 = self.PatterHexa_16bit(seek_img16)

            if self.CorrectBadPixels.isChecked():
                bad_pixels = self.FindBadPixel(seek_img16)
                seek_img16 = self.CorrectBadPixel(bad_pixels, seek_img16)
                print len(bad_pixels)

            seek_img8 = ((seek_img16 - seek_img16.min()) / (seek_img16.ptp() / 255.0)).astype(numpy.uint8)     #Visualizacion
            qImg = QImage(seek_img8, 208, 156, QtGui.QImage.Format_Indexed8)                                   #Visualizacion
            self.buff_qimg = qImg                                                                              #Visualizacion
            self.label.setPixmap(QtGui.QPixmap.fromImage(qImg))                                                #Visualizacion
            print self.show_frame()                                                                            #Visualizacion


    def show_frame(self):
        global fps_t
        global fps_f
        now = int(time.time())
        fps_f += 1
        if fps_t == 0:
            fps_t = now
        elif fps_t < now:
            print '\rFPS: %.2f' % (1.0 * fps_f / (now - fps_t))
            fps_t = now
            fps_f = 0

    def rec_image(self):
        global i
        rec_img16 = cam_connect.get_image()
        rec_img16 = self.PatterHexa_16bit(rec_img16)
        i += 1
        if not os.path.exists('./images'):
            os.makedirs('./images')
        name_img = './images/thermalseek_%d.tiff' % (i,)
        scipy.misc.imsave(name_img, rec_img16)

    def StartSeek(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.Adq)
        self.timer.start(1000. / 30)

    def Starthist(self):
        self.timer3 = QtCore.QTimer()
        self.timer3.timeout.connect(self.histogram)
        self.timer3.start(1000. / 30)

    def RecStop(self, pressed):
        if pressed:
            print 'play'
            self.pushButton.setText('stop')
            self.timer2 = QtCore.QTimer()
            self.timer2.timeout.connect(self.rec_image)
            self.timer2.start(1000. / 30)

        else:
            print 'stop'
            self.pushButton.setText('rec')
            self.timer2.stop()

    def PatterHexa_16bit(self, img):
        col = 0
        row_ini = 0
        col_ini = 10
        array = img

        for row in range(row_ini, 155, 1):
            for col in range(col_ini, 207, 15):
                sum_near = array[row - 1, col - 1] + array[row - 1, col + 1] + \
                           array[row + 1, col - 1] + array[row + 1, col + 1]  # Suma de los Pixeles Vecinos
                mean_interp = sum_near / 4                                    # Promedio de la suma
                array[row, col] = mean_interp                                 # Se asigna el valor

            col_ini = col + 8                                                 # Salto de 8 Pixeles para la siguiente Fila
            col_ini -= 207                                                    # Menos 207 para para el indice que empieza en la siguiente fila
            if col_ini > 207:
                col_ini += 15
        return array

    def FindBadPixel(self, img):
        bad_pixels = []
        array = img
        max_value = array.max()
        min_value = array.min()
        range_noise_up = max_value - (max_value * 0.1)
        range_noise_down = min_value + (max_value * 0.1)
        print max_value, min_value, range_noise_down
        for row in range(1, 155, 1):
            for col in range(1, 206, 1):
                if array[row, col] > range_noise_up:
                    bad_pixels.append((row, col))
        return bad_pixels

    def CorrectBadPixel(self, bad_pixels, img):
        noiseReduction = 100
        array = img
        for bp in bad_pixels:
            row = bp[0]
            col = bp[1]
            mean_near = (array[row - 1, col - 1] + array[row - 1, col + 1] +
                              array[row + 1, col - 1] + array[row + 1, col + 1]) / 4
            if (mean_near - array[row, col]) > noiseReduction:
                array[row, col] = mean_near
        return array

    def histogram(self):
        #rec_img16 = cam_connect.get_image()
        #plt.hist(rec_img16, facecolor='green', alpha=0.75)
        #plt.show()
        pass



app = QtGui.QApplication(sys.argv)
MyWindow = MyWindowClass(None)
MyWindow.show()
MyWindow.StartSeek()
MyWindow.Starthist()
app.exec_()
