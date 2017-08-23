from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import *
import scipy.misc
import time
from connectseek import *
import sys
import numpy
import os

cam_connect = ConnectSeek()
cam_connect.query()
form_class = uic.loadUiType("cam.ui")[0]

i = 0
fps_t = 0
fps_f = 0


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
        seek_img8, seek_img16 = cam_connect.get_image()
        if self.CorrectPatternHexa.isChecked():
            seek_img8 = self.PatterHexa_8bit(seek_img8)
        qImg = QImage(seek_img8, 208, 156, QtGui.QImage.Format_Indexed8)
        self.buff_qimg = qImg
        self.label.setPixmap(QtGui.QPixmap.fromImage(qImg))
        print self.show_frame()

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
        rec_img8, rec_img16 = cam_connect.get_image()
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

    def PatterHexa_8bit(self, img):
        col = 0
        row_ini = 0
        col_ini = 10
        array = numpy.array(img, dtype='uint16')                                    #Conversion de entero 8 bit a  entero 16 bit

        for row in range(row_ini, 155, 1):
            for col in range(col_ini, 207, 15):
                sum_near = array[row - 1, col - 1] + array[row - 1, col + 1] + \
                              array[row + 1, col - 1] + array[row + 1, col + 1]     #Suma de los Pixeles Vecinos
                mean_interp = sum_near / 4                                          # Promedio de la suma
                array[row, col] = mean_interp                                       # Se asigna el valor

            col_ini = col + 8                                                       #Salto de 8 Pixeles para la siguiente Fila
            col_ini -= 207                                                          # Menos 207 para para el indice que empieza en la siguiente fila
            if col_ini > 207:
                col_ini += 15

        array = numpy.array(array, dtype='uint8')
        return array

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

    def BadPixel(self, img_8):
        noise_reduction = 25                                                  # Valor seteable
        array = numpy.array(img_8, dtype='uint16')                            # Conversion de entero 8 bit a  entero 16 bit
        array_color = [0,0,0,0]
        for row in range(0, 154, 1):
            for col in range(0, 206, 1):
                array_color[0] = array[row, col + 1]
                array_color[1] = array[row + 2, col + 1]
                array_color[2] = array[row + 1, col]
                array_color[3] = array[row + 1, col + 2]

                avgValue = (numpy.sum(array_color) - (numpy.max(array_color) + numpy.min(array_color))) / 2

                center_pixel = array[row + 1, col + 1]
                if (avgValue - center_pixel) > noise_reduction:
                    array[row + 1, col + 1] = avgValue
        array_badpixel = numpy.array(array, dtype='uint8')
        return array_badpixel


app = QtGui.QApplication(sys.argv)
MyWindow = MyWindowClass(None)
MyWindow.show()
MyWindow.StartSeek()
app.exec_()
