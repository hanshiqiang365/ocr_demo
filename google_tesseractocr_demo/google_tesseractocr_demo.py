#author: hanshiqiang365 （微信公众号：韩思工作室）

import os,sys,time
import traceback
import pygame

from PyQt5.QtCore import QThread, QSize
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon

import sys, io
import pyocr.builders
from wand.image import Image as wandImage
from PIL import Image as pillowIMage

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def romoverepetedlinebreak(str):
    resultStr = str
    tempStr = ''
    strList = list(resultStr)

    for i in range(len(strList)):
        if strList[i] != '\n':
            tempStr += strList[i]
        elif strList[i] == '\n' and i+1 ==len(strList):
            tempStr += strList[i]
        elif strList[i] == '\n' and strList[i+1] !='\n':
            tempStr += strList[i]
        else: continue

    return tempStr

g_log = None

class LogHandler(QtCore.QObject):
    show = QtCore.pyqtSignal(str)

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.browseButton = self.createButton("&浏览...", self.browse)
        self.transButton = self.createButton("&开始OCR识别", self.ocrConvert)

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

        self.setWindowTitle("Google Tesseract OCR Tool——Developed by hanshiqiang365 （微信公众号：韩思工作室）")
        self.resize(800, 600)

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

    def ocrConvert(self):
        fileName = self.fileComboBox.currentText()
        if not fileName:
            self.logger.show.emit('请先选择要识别的Image或PDF文档')
            return

        self.logger.show.emit('开始OCR识别：{}'.format(fileName))

        tool = pyocr.get_available_tools()[0]
        pdf_file=fileName

        req_image = []

        ima_pdf = wandImage(filename=pdf_file, resolution=300)
        image_jpeg = ima_pdf.convert('jpeg')

        for img in image_jpeg.sequence:
            img_page = wandImage(image=img)
            img_page.type = 'grayscale'
            req_image.append(img_page.make_blob('jpeg'))

        page_number = 0
        final_text=""

        for img in req_image:
            text = tool.image_to_string(
                pillowIMage.open(io.BytesIO(img)),
                lang='jpn+eng+chi_sim',
                builder=pyocr.builders.TextBuilder()
                )
            page_number = page_number + 1
            final_text=final_text+"Page-"+str(f'{page_number}')+"\r\n"+text+"\r\n"
            self.logger.show.emit("Page-"+str(f'{page_number}')+"："+text)

        final_text = romoverepetedlinebreak(final_text).replace('\n','\r\n')

        with open(f'{pdf_file}.txt', 'wb') as f:
            f.write(final_text.encode('utf-8'))

        
        self.logger.show.emit('OCR识别完成')

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
