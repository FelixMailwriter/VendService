# -*- coding:utf-8 -*-

import os
from PyQt4 import uic
from PyQt4.Qt import QObject
from PyQt4 import QtCore
from Objects import ObjHandler
from Magazines import MagazinesController
from Report import ReportController


class HApp(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.form=MainWindow()
        self.ObjHandler=ObjHandler(self.form)
        self.MagazinesController=None
        self.ReportController=None
        self.form.window.tabWidget.currentChanged.connect(self.tabSwitchHandler)
        self.form.window.show()
        
        
    def tabSwitchHandler(self, tabNum):
        if tabNum==0:
            self.ObjHandler=ObjHandler(self.form)
        elif tabNum==1:
            self.MagazinesController=MagazinesController(self.form)
        elif tabNum==2:
            self.ReportController=ReportController(self.form)
        
class MainWindow(QObject):

    def __init__(self):
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/mainForm.ui")
        self.window=uic.loadUi(path)
        self.magController=None
  
    def refreshMagazinesTable(self):
        pass              
                  
                  