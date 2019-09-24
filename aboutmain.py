import os
import os.path
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget
import aboutgui
import licensemain
import anaxcel


class abouthandel(QtWidgets.QMainWindow, aboutgui.Ui_MainWindow):
    switch_window2 = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(abouthandel, self).__init__(parent)
        if getattr(sys, 'frozen', False):
            self.frozen = 'ever so'
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + 'icons/icon.png'))
        self.setStyleSheet(open("Dark/darkstyle.qss", "r").read())
        self.pushButton.clicked.connect(self.showLicense)
        self.label_4.setOpenExternalLinks(True)
        self.label_5.setOpenExternalLinks(True)
        self.setWindowFlags(self.windowFlags() | Qt.Popup | Qt.WindowStaysOnTopHint)
        self.center()

    def showLicense(self):
        self.window = licensemain.licensehandel()
        self.window.show()

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())