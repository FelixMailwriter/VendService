# -*- coding:utf-8 -*-

import os
from PyQt4 import QtCore, uic
from PyQt4.Qt import QObject, QFont, QHeaderView, QComboBox, QStringList
from PyQt4 import QtGui
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
        self.MagazinsTable=self.window.tblw_Magazines
        self.ItemsList=QStringList()
        self.setUpTables()
    
    def setItemsList(self, itemsNames):
        self.ItemsList=itemsNames
        
        #self.ItemsList.addItems(itemsNames)
        #self.window.cmbx_Mag.addItems(itemsNames)
        
        
        #i=self.window.cmbx_Mag.findText(u'ff')
        #self.window.cmbx_Mag.setCurrentIndex(i)
        
    def setUpTables(self):
        rowsFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.MagazinsTable.setFont(rowsFont)
        headerFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.MagazinsTable.horizontalHeader().setFont(headerFont) 
        self.MagazinsTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.MagazinsTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        self.MagazinsTable.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
        self.MagazinsTable.horizontalHeader().setResizeMode(3,QHeaderView.Stretch)
        self.MagazinsTable.verticalHeader().hide()
        
        self.ItemTable.setFont(rowsFont)
        self.ItemTable.horizontalHeader().setFont(headerFont) 
        self.ItemTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.ItemTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        self.ItemTable.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
        self.ItemTable.verticalHeader().hide()
               
    def fillItemsTable(self, rows):
        self.ItemTable.setRowCount(0)
        counter=0
        for row in rows:
            ItemIdItem=QtGui.QTableWidgetItem(str(row[0]))
            ItemIdItem.setTextAlignment(QtCore.Qt.AlignCenter)
            ItemName=QtGui.QTableWidgetItem(row[1])
            ItemName.setTextAlignment(QtCore.Qt.AlignCenter)
            ItemPrice=QtGui.QTableWidgetItem(str(row[2]/100.0))
            ItemPrice.setTextAlignment(QtCore.Qt.AlignCenter)
            

            self.ItemTable.insertRow(counter)
            self.ItemTable.setItem(counter,0,ItemIdItem)
            self.ItemTable.setItem(counter,1,ItemName)
            self.ItemTable.setItem(counter,2,ItemPrice)
            counter+=1             
    
    def getCurrentItems(self):
        return self.ItemTable.selectedItems()
                   
    def setIcon(self, qpixmap):
        self.window.ibl_ItemIcon.setPixmap(qpixmap) 
        
    def fillMagazinsTable(self, rows):
        self.MagazinsTable.setRowCount(0)
        counter=0
        for row in rows:
            ItemIdMag=QtGui.QTableWidgetItem(str(str(row[0])))
            ItemIdMag.setTextAlignment(QtCore.Qt.AlignCenter)
            
            cmbx=QComboBox()
            cmbx.addItems(self.ItemsList)
            name=str(row[2])
            index=cmbx.findText(name)
            cmbx.setCurrentIndex(index)
            #ItemName=QtGui.QTableWidgetItem(str(row[1]))
            #ItemName.setTextAlignment(QtCore.Qt.AlignCenter)
            ItemItemQty=QtGui.QTableWidgetItem(str(row[2]))
            ItemItemQty.setTextAlignment(QtCore.Qt.AlignCenter)
            ItemIdItem=QtGui.QTableWidgetItem(str(row[3]))
            ItemIdItem.setTextAlignment(QtCore.Qt.AlignCenter)

            self.MagazinsTable.insertRow(counter)
            self.MagazinsTable.setItem(counter,0,ItemIdMag)
            self.MagazinsTable.setItem(counter,1,cmbx)
            self.MagazinsTable.setItem(counter,2,ItemItemQty)
            self.MagazinsTable.setItem(counter,3,ItemIdItem)
            counter+=1            

                          
                  