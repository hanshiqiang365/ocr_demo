#author: hanshiqiang365 （微信公众号：韩思工作室）

import os,sys,time
import traceback
import pygame

from PyQt5.QtCore import QThread, QSize
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon

from pyzbar import pyzbar
import matplotlib.pyplot as plt
import cv2

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

g_log = None

class LogHandler(QtCore.QObject):
    show = QtCore.pyqtSignal(str)

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.browseButton = self.createButton("&浏览...", self.browse)
        self.transButton = self.createButton(" &开始QRcode和Barcode识别 ", self.qrcodeReader)

        self.fileComboBox = self.createComboBox('file')

        docLabel = QtWidgets.QLabel("选择文件:")
        self.filesFoundLabel = QtWidgets.QLabel()

        self.logPlainText = QtWidgets.QPlainTextEdit()
        self.logPlainText.setReadOnly(True)


        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.transButton)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(docLabel, 0, 0)
        mainLayout.addWidget(self.fileComboBox, 0, 1)
        mainLayout.addWidget(self.browseButton, 0, 2)
        mainLayout.addWidget(self.logPlainText, 1, 0, 1, 3)
        mainLayout.addWidget(self.filesFoundLabel, 2, 0)
        mainLayout.addLayout(buttonsLayout, 3, 0, 1, 3)
        self.setLayout(mainLayout)

        #pygame.mixer.init()
        #pygame.mixer.music.load("demo_bgm.wav")
        #pygame.mixer.music.play(-1)

        app_icon = QIcon()
        icon_path = resource_path('demo_icon.jpg')
        app_icon.addFile(icon_path, QSize(16, 16))
        app_icon.addFile(icon_path, QSize(24, 24))
        app_icon.addFile(icon_path, QSize(32, 32))
        app_icon.addFile(icon_path, QSize(48, 48))
        app_icon.addFile(icon_path, QSize(256, 256))
        self.setWindowIcon(app_icon)

        self.setWindowTitle("QR Code & Barcode Reader Tool——Developed by hanshiqiang365 （微信公众号：韩思工作室）")
        self.resize(800, 300)

        self.logger = LogHandler()
        self.logger.show.connect(self.onLog)
        g_log = self.logger

    def browse(self):
        sfile, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择文件",
            QtCore.QDir.currentPath(),
            "PNG, BMP, JPG, PDF(*.png *.jpg *.bmp *.pdf *.PDF)",
        )
        print(sfile)

        if sfile:
            self.logPlainText.clear()
            msg = '选择了文件: <b>{}</b>'.format(sfile)
            self.logger.show.emit(msg)
            if self.fileComboBox.findText(sfile) == -1:
                self.fileComboBox.addItem(sfile)

            self.fileComboBox.setCurrentIndex(self.fileComboBox.findText(sfile))

    def onLog(self, msg):
        self.logPlainText.appendHtml(msg)


    def qrcodeReader(self):
        fileName = self.fileComboBox.currentText()
        if not fileName:
            self.logger.show.emit('请先选择要识别的Image或PDF文档')
            return

        self.logger.show.emit('开始QRcode和Barcode识别：{}'.format(fileName))

        image = cv2.imread(fileName)
        barcodes = pyzbar.decode(image)

        for barcode in barcodes:
            (x, y, w, h) = barcode.rect

            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,.8, (255, 0, 0), 2)

            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            self.logger.show.emit("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

        self.logger.show.emit('QRcode和Barcode识别完成')

    def createButton(self, text, member):
        button = QtWidgets.QPushButton(text)
        button.clicked.connect(member)
        return button

    def createComboBox(self, btype=''):
        comboBox = QtWidgets.QComboBox(self)
        comboBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred)
        return comboBox

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
