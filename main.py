# -*- coding:utf-8 -*-
from PyQt4 import QtGui
import sys
from BLL import HApp

if __name__ == '__main__':
    app=QtGui.QApplication(sys.argv)
    HApp=HApp.HApp()
    sys.exit(app.exec_())