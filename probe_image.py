from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import cv2

class Ventana(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        contenedor = QVBoxLayout()
        self.setLayout(contenedor)

        btnSalir = QPushButton("Salir", None)
        contenedor.addWidget(btnSalir)
        self.connect(btnSalir, SIGNAL("clicked()"), self.salir)

    def salir(self):
        exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec_())