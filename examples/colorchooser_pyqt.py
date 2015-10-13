#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from sense_hat import SenseHat

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class MyColorDialog(QtGui.QColorDialog):
    def __init__(self, *args, **kwargs):
        super(MyColorDialog, self).__init__(*args, **kwargs) 
        self.currentColorChanged.connect(self.color_changed)
        self.sense = SenseHat()
        self.init_lcd()

    def color_changed(self, color):
        t_RGBA = color.getRgb() # (r, g, b, a)
        t_RGB = t_RGBA[0:3]
        for x in range(8):
            for y in range(8):
                self.sense.set_pixel(x, y, *t_RGB)

    def init_lcd(self):
        for x in range(8):
            for y in range(8):
                self.sense.set_pixel(x, y, 255, 255, 255)

def main():
    app = QtGui.QApplication(sys.argv)
    color_dlg = MyColorDialog()
    color_dlg.open()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
