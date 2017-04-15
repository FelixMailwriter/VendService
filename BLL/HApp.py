# -*- coding:utf-8 -*-

import os
from PyQt4 import uic
from PyQt4.Qt import QObject
from PyQt4 import QtCore
from Objects import ObjHandler
from Magazines import MagazinesController


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
        self.window.tabWidget.currentChanged.connect(self.tabChanged)
     
    def addItem(self):
        self.emit(QtCore.SIGNAL("AddItemClicked"))    
                  
    def editItem(self):
        self.emit(QtCore.SIGNAL("EditItemClicked")) 
        
    def tabChanged(self):
        if self.window.tabWidget.currentIndex()==0:
           pass 
        if self.window.tabWidget.currentIndex()==1:
            self.refreshMagazinesTable()
        if self.window.tabWidget.currentIndex()==2:
            pass
    
    
    def refreshMagazinesTable(self):
        pass              
                  
                  