#!/usr/bin/python3
# -*- coding: utf-8 -*-

import ctypes
import math
import os
import sys
import threading
import time

import urllib3
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import readonly_resource

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/63.0.3239.132 Safari/537.36'}


def hideConsole():
    """
    Hides the console window in GUI mode. Necessary for frozen application, because
    this application support both, command line processing AND GUI mode and theirfor
    cannot be run via pythonw.exe.
    """
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        # if you wanted to close the handles...
        # ctypes.windll.kernel32.CloseHandle(whnd)


def showConsole():
    """Unhides console window"""
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 1)


async def async_function():
    time.sleep(2)
    return 1


class downloadThread (threading.Thread):
    def __init__(self, idd, s, e, xmin, ymin, xmax, ymax, num, prox):
        threading.Thread.__init__(self)
        self.id = idd
        self.s = s
        self.e = e
        self.xmin = min(xmin, xmax)
        self.ymin = min(ymin, ymax)
        self.xmax = max(xmin, xmax)
        self.ymax = max(ymin, ymax)
        self.num = num
        self.prox = prox

    def run(self):
        for i in range(self.s, self.e):
            savepath = "./" + str(i) + "/"
            try:
                if (os.path.exists(savepath) == 0):
                    os.makedirs(savepath)
            except:
                pass
            if ((int(pow(2, i) * self.ymax) - int(pow(2, i) * self.ymin)) <= self.num and self.id < (int(pow(2, i) * self.ymax) - int(pow(2, i) * self.ymin))):
                ss = self.id + int(pow(2, i) * self.ymin)
                ee = ss + 1
            elif ((int(pow(2, i) * self.ymax) - int(pow(2, i) * self.ymin)) > self.num):
                ss = (self.id * (int(pow(2, i) * self.ymax) - int(pow(2, i)
                      * self.ymin))) // self.num + int(pow(2, i) * self.ymin)
                ee = ((self.id + 1) * (int(pow(2, i) * self.ymax) - int(pow(2, i)
                      * self.ymin))) // self.num + int(pow(2, i) * self.ymin)
            else:
                ss = ee = 0
            for j in range(ss, ee):
                for k in range(int(pow(2, i) * self.xmin), int(pow(2, i) * self.xmax)):
                    if (os.path.exists(savepath + str(k) + "_" + str(j) + ".jpg") == False):
                        url = "https://mts0.googleapis.com/vt?lyrs=s&x=" + \
                            str(k) + "&y=" + str(j) + "&z=" + str(i)
                        try:
                            filename = str(k) + "_" + str(j) + ".jpg"
                            proxy = urllib3.ProxyManager(self.prox, headers=header)

                            with open(savepath + filename, 'wb') as f:
                                f.write(proxy.request('GET', url, retries=3, timeout=urllib3.Timeout(connect=45, read=240)).data)
                                f.close()
                            print(filename + "_下载完成")
                        except:
                            print(str(k) + "_" + str(j) + "_获取失败")


def start_thread(s, e, xmin, ymin, xmax, ymax, threadnum, prox):
    threadlist = []
    for i in range(threadnum):
        threadlist.append(downloadThread(
            i, s, e, xmin, ymin, xmax, ymax, threadnum, prox))
        threadlist[i].start()

    for i in threadlist:
        i.join()


def combine_img(s, e, xmin, ymin, xmax, ymax):
    for i in range(s, e):
        dest_im = Image.new('RGBA', ((int(pow(2, i) * xmax) - int(pow(2, i) * xmin)) *
                            256, (int(pow(2, i) * ymax) - int(pow(2, i) * ymin)) * 256), (255, 255, 255))
        dest_im.save(str(i) + ".png", 'png')
        for j in range(int(pow(2, i) * ymax) - int(pow(2, i) * ymin)):
            for k in range(int(pow(2, i) * xmax) - int(pow(2, i) * xmin)):
                savepath = "./" + str(i) + "/"
                filename = str(k + int(pow(2, i) * xmin)) + "_" + \
                    str(j + int(pow(2, i) * ymin)) + ".jpg"
                src_im = Image.open(savepath+filename)
                dest_im.paste(src_im, (k * 256, j * 256))
        dest_im.save(str(i) + ".png", 'png')


class MainUi(QMainWindow):

    def __init__(self):
        super().__init__()
        self.conn = None
        self.BtnList = {}
        self.TitleList = {}
        self.TextEditList = {}
        self.initUI()  # 界面绘制交给InitUi方法

    def initUI(self):
        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        self.dpi = ctypes.windll.gdi32.GetDeviceCaps(
            ctypes.windll.user32.GetDC(0), 88)
        self.ratio = self.dpi/96
        self.height = int(self.ratio*self.screenRect.width()*16/80+0.5)
        self.width = int(self.ratio*self.screenRect.width()*12/80+0.5)
        self.unit = int(self.ratio*self.screenRect.width()/240+0.5)

        font = QFont()
        font.setPointSize(int(self.unit/self.ratio))

        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWindow")
        self.setCentralWidget(self.main_widget)

        self.main_widget.setStyleSheet(
            "QWidget#MainWindow{border-image:url(:/readonly.png);}")
        self.setWindowOpacity(0.9)
        self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setStyleSheet(
            ''' QWidget{color:#232C51; background:rgba(255,255,255,192); border:1px solid darkGray; border-radius:'''+str(self.unit)+'''px;}''')

        close = QPushButton("")  # 关闭按钮
        large = QPushButton("")  # 最大化按钮
        mini = QPushButton("")  # 最小化按钮
        close.setFixedSize(2*self.unit, 2*self.unit)
        large.setFixedSize(2*self.unit, 2*self.unit)
        mini.setFixedSize(2*self.unit, 2*self.unit)
        close.setStyleSheet(
            '''QPushButton{background:#F76677;border-radius:'''+str(self.unit)+'''px;}QPushButton:hover{background:red;}''')
        large.setStyleSheet(
            '''QPushButton{background:#F7D674;border-radius:'''+str(self.unit)+'''px;}QPushButton:hover{background:#F7C604;}''')
        mini.setStyleSheet(
            '''QPushButton{background:#6DDF6D;border-radius:'''+str(self.unit)+'''px;}QPushButton:hover{background:#0DDF0D;}''')
        close.clicked.connect(QCoreApplication.instance().quit)
        mini.clicked.connect(self.showMinimized)
        large.clicked.connect(self.windowCtl)

        title0 = QLabel('    GoogleMap Downloader    ')
        title0.setFont(font)
        title0_1 = QLabel(' 代理(留空不代理) ')
        title0_1.setFont(font)
        title1 = QLabel(' 下载线程数 ')
        title1.setFont(font)
        title2 = QLabel(' 纬度范围 ')
        title2.setFont(font)
        title3 = QLabel(' 经度范围 ')
        title3.setFont(font)
        title4 = QLabel(' 图像等级范围 ')
        title4.setFont(font)
        title0_1.setFixedSize(16*self.unit, int(2.25*self.unit+0.5))
        title1.setFixedSize(16*self.unit, int(2.25*self.unit+0.5))
        title2.setFixedSize(16*self.unit, int(2.25*self.unit+0.5))
        title3.setFixedSize(16*self.unit, int(2.25*self.unit+0.5))
        title4.setFixedSize(16*self.unit, int(2.25*self.unit+0.5))

        text0 = QLineEdit()
        text1 = QLineEdit()
        text2 = QLineEdit()
        text3 = QLineEdit()
        text4 = QLineEdit()
        text5 = QLineEdit()
        text6 = QLineEdit()
        text7 = QLineEdit()
        text0.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text0.setFont(font)
        text1.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text1.setFont(font)
        text2.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text2.setFont(font)
        text3.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text3.setFont(font)
        text4.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text4.setFont(font)
        text5.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text5.setFont(font)
        text6.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text6.setFont(font)
        text7.setStyleSheet(
            '''QLineEdit{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}''')
        text7.setFont(font)
        text0.setText("http://127.0.0.1:7890/")
        text1.setText("96")
        text2.setText("22.545516186068134")
        text3.setText("22.54715163092838")
        text4.setText("114.05203219450112")
        text5.setText("114.0570653363287")
        text6.setText("20")
        text7.setText("22")
        self.TextEditList['text0'] = text0
        self.TextEditList['text1'] = text1
        self.TextEditList['text2'] = text2
        self.TextEditList['text3'] = text3
        self.TextEditList['text4'] = text4
        self.TextEditList['text5'] = text5
        self.TextEditList['text6'] = text6
        self.TextEditList['text7'] = text7

        btn1 = QPushButton(" 下载图像 ", self)
        btn2 = QPushButton(" 合并图像 ", self)
        self.BtnList['btn1'] = btn1
        self.BtnList['btn2'] = btn2
        btn1.setStyleSheet('''QPushButton{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}
                               QPushButton:hover{border:1px solid darkGray; border-radius:'''+str(self.unit)+'''px; background:rgba(211,211,211,192);}''')
        btn2.setStyleSheet('''QPushButton{border:1px solid darkGray;height:'''+str(3*self.unit)+'''px;width:'''+str(10*self.unit)+'''px;}
                               QPushButton:hover{border:1px solid darkGray; border-radius:'''+str(self.unit)+'''px; background:rgba(211,211,211,192);}''')
        btn1.setFont(font)
        btn2.setFont(font)

        btn1.clicked.connect(self.buttonClicked)
        btn2.clicked.connect(self.buttonClicked)

        hbox0 = QHBoxLayout()
        hbox0.addStretch(1)
        hbox0.addWidget(title0)
        hbox0.addStretch(1)
        hbox0.addWidget(mini)
        hbox0.addWidget(large)
        hbox0.addWidget(close)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(text2)
        hbox1.addWidget(text3)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(text4)
        hbox2.addWidget(text5)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(text6)
        hbox3.addWidget(text7)

        hbox4 = QHBoxLayout()
        hbox4.addStretch(1)
        hbox4.addWidget(btn1)
        hbox4.addStretch(1)
        hbox4.addWidget(btn2)
        hbox4.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox0)
        vbox.addWidget(title0_1)
        vbox.addWidget(text0)
        vbox.addWidget(title1)
        vbox.addWidget(text1)
        vbox.addWidget(title2)
        vbox.addLayout(hbox1)
        vbox.addWidget(title3)
        vbox.addLayout(hbox2)
        vbox.addWidget(title4)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)

        self.main_widget.setLayout(vbox)
        self.setGeometry(200, 200, self.width, self.height)
        self.setWindowTitle('readonly')
        self.setWindowIcon(QIcon(':/readonly.ico'))

    def buttonClicked(self):
        sender = self.sender()
        if(sender == self.BtnList['btn1']):
            try:
                threadnum = int(self.TextEditList["text1"].text())
                maxlat = float(self.TextEditList["text2"].text())
                minlat = float(self.TextEditList["text3"].text())
                minlng = float(self.TextEditList["text4"].text())
                maxlng = float(self.TextEditList["text5"].text())
                s = int(self.TextEditList["text6"].text())
                e = int(self.TextEditList["text7"].text())
                prox = self.TextEditList["text0"].text()
                # 除以2指数后的xmin,下同,即此参数需乘以2指数后可用
                xmin = ((minlng + 180.0) / 360.0)
                ymin = (
                    (math.pi - math.asinh(math.tan(minlat * math.pi / 180)))/(2 * math.pi))
                xmax = ((maxlng + 180.0) / 360.0)
                ymax = (
                    (math.pi - math.asinh(math.tan(maxlat * math.pi / 180)))/(2 * math.pi))

                start_thread(s, e, xmin, ymin, xmax, ymax, threadnum, prox)
            except:
                pass
        if(sender == self.BtnList['btn2']):
            try:
                maxlat = float(self.TextEditList["text2"].text())
                minlat = float(self.TextEditList["text3"].text())
                minlng = float(self.TextEditList["text4"].text())
                maxlng = float(self.TextEditList["text5"].text())
                s = int(self.TextEditList["text6"].text())
                e = int(self.TextEditList["text7"].text())
                # 除以2指数后的xmin,下同,即此参数需乘以2指数后可用
                xmin = ((minlng + 180.0) / 360.0)
                ymin = (
                    (math.pi - math.asinh(math.tan(minlat * math.pi / 180)))/(2 * math.pi))
                xmax = ((maxlng + 180.0) / 360.0)
                ymax = (
                    (math.pi - math.asinh(math.tan(maxlat * math.pi / 180)))/(2 * math.pi))

                combine_img(s, e, xmin, ymin, xmax, ymax)
            except:
                pass

    def restore(self):
        pass

    def windowCtl(self):
        if(self.isMaximized()):
            self.showNormal()
        else:
            self.showMaximized()

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        self._endPos = e.pos() - self._startPos
        self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None


if __name__ == '__main__':
    ctypes.windll.user32.SetProcessDPIAware()
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    mui = MainUi()
    mui.show()
    sys.exit(app.exec_())
