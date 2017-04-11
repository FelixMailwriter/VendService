# -*- coding:utf-8 -*-

import os
from Objects import ObjHandler
from PyQt4 import uic
from PyQt4.Qt import QObject

class HApp():

    def __init__(self):
        self.window=MainWindow()
        self.window.window.show()
        self.ObjHandler=ObjHandler(self.window)
        self.ObjHandler.getItems()
        
class MainWindow(QObject):

    def __init__(self):
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/mainForm.ui")
        self.window=uic.loadUi(path)
        
        