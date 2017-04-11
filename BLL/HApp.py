# -*- coding:utf-8 -*-

import os
from Objects import ObjHandler
from PyQt4 import uic
from PyQt4.Qt import QObject
from PyQt4 import QtCore

class HApp():

    def __init__(self):
        
        self.form=MainWindow()
        self.form.window.show()
        self.ObjHandler=ObjHandler(self.form)
        self.ObjHandler.getItems()
        
class MainWindow(QObject):

    def __init__(self):
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/mainForm.ui")
        self.window=uic.loadUi(path)
        self.window.btn_AddItem.clicked.connect(self.addItem)
        self.window.btn_EditItem.clicked.connect(self.editItem)
     
    def addItem(self):
        self.emit(QtCore.SIGNAL("AddItemClicked"))    
                  
    def editItem(self):
        self.emit(QtCore.SIGNAL("EditItemClicked")) 
                  
                  
                  