# -*- coding:utf-8 -*-
import os
from PyQt4 import uic
from PyQt4.Qt import QObject

class Errors(QObject):

    def __init__(self, messageText):
        QObject.__init__(self)
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/errorWindow.ui")
        self.window=uic.loadUi(path)
        self.window.btn_close.clicked.connect(self.window.close)
        self.window.label.setText(messageText)
        
    def setMessageText(self, messageText):
        self.window.label.setText(messageText)
        