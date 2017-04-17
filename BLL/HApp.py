# -*- coding:utf-8 -*-

import os
from PyQt4 import uic
from PyQt4.Qt import QObject, QMessageBox
from PyQt4 import QtCore, QtGui
from BLL.ItemsController import ItemsController
from Magazines import MagazinesController
from Report import ReportController


class HApp(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.form=MainWindow()
        self.ItemsController=ItemsController(self.form)
        self.MagazinesController=MagazinesController(self.form)
        self.ReportController=ReportController(self.form)
        self.form.window.show()
        
class MainWindow(QObject):

    def __init__(self):
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/mainForm.ui")
        self.window=uic.loadUi(path)
        self.ItemTable=self.window.ItemTable

        
        
    def fillItemsTable(self, rows):
        self.ItemTable.setRowCount(0)
        counter=0
        for row in rows:
            Item0=QtGui.QTableWidgetItem(str(row[0]))
            Item1=QtGui.QTableWidgetItem(row[1])
            Item2=QtGui.QTableWidgetItem(str(row[2]/100.0))

            self.ItemTable.insertRow(counter)
            self.ItemTable.setItem(counter,0,Item0)
            self.ItemTable.setItem(counter,1,Item1)
            self.ItemTable.setItem(counter,2,Item2)
            counter+=1             
    
    def getCurrentItems(self):
        return self.ItemTable.selectedItems()
                   
    def setIcon(self, qpixmap):
        self.window.ibl_ItemIcon.setPixmap(qpixmap)    

                          
                  