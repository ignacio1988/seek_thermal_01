# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cam.ui'

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_WEBCAM(object):
    def setupUi(self, WEBCAM):
        WEBCAM.setObjectName(_fromUtf8("WEBCAM"))
        WEBCAM.resize(450, 356)
        self.centralwidget = QtGui.QWidget(WEBCAM)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(190, 40, 211, 181))
        self.label.setAutoFillBackground(False)
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 40, 111, 50))
        self.pushButton.setCheckable(True)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.CorrectPatternHexa = QtGui.QCheckBox(self.centralwidget)
        self.CorrectPatternHexa.setGeometry(QtCore.QRect(10, 280, 191, 22))
        self.CorrectPatternHexa.setObjectName(_fromUtf8("CorrectPatternHexa"))
        WEBCAM.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(WEBCAM)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 450, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuSeekThermalApp = QtGui.QMenu(self.menubar)
        self.menuSeekThermalApp.setObjectName(_fromUtf8("menuSeekThermalApp"))
        WEBCAM.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(WEBCAM)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        WEBCAM.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuSeekThermalApp.menuAction())

        self.retranslateUi(WEBCAM)
        QtCore.QMetaObject.connectSlotsByName(WEBCAM)

    def retranslateUi(self, WEBCAM):
        WEBCAM.setWindowTitle(_translate("WEBCAM", "MainWindow", None))
        self.pushButton.setText(_translate("WEBCAM", "Rec", None))
        self.CorrectPatternHexa.setText(_translate("WEBCAM", "Correción Patrón Hexagonal", None))
        self.menuSeekThermalApp.setTitle(_translate("WEBCAM", "SeekThermalApp", None))

