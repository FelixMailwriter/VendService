# -*- coding:utf-8 -*-

import Errors
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QObject, QMessageBox 
from DAL.DBConnector import DbConnector
import base64
import EditItem


class ObjHandler(QObject):
    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.ItemTable=self.form.window.ItemTable
        self.ItemTable.cellClicked.connect(self.refreshIcon)
        self.errWindow=Errors.Errors("")
        self.connect(self.form, QtCore.SIGNAL("AddItemClicked"), self.addItem)
        self.connect(self.form, QtCore.SIGNAL("EditItemClicked"), self.editItem)
        
    def getItems(self):
        self.ItemTable.setRowCount(0)
        rows=self.DbConnector.getItems()
        counter=0
        for row in rows:
            Item0=QtGui.QTableWidgetItem(str(row[0]))
            Item1=QtGui.QTableWidgetItem(row[1])
            Item2=QtGui.QTableWidgetItem(str(row[2]))

            self.ItemTable.insertRow(counter)
            self.ItemTable.setItem(counter,0,Item0)
            self.ItemTable.setItem(counter,1,Item1)
            self.ItemTable.setItem(counter,2,Item2)
            counter+=1
            
    def refreshIcon(self, row):
        Items=self.ItemTable.selectedItems()
        idItem=int(Items[0].text())
        conn=self.DbConnector.getConnection()
        cur=conn.cursor()
        cur.execute('SELECT ItemIcon from Items where idItem={}'.format(idItem))
        result=cur.fetchone()[0]
        picBytes = base64.b64decode(result)
        qpixmap=QtGui.QPixmap()
        qpixmap.loadFromData(picBytes)
        self.form.window.ibl_ItemIcon.setPixmap(qpixmap)

    def addItem(self):
        count=self.ItemTable.rowCount()+1
        self.ItemTable.insertRow(count)
        param={}
        param["itemId"]=0
        param["itemName"]=""
        param["itemPrice"]=""
        param["itemIcon"]=QtGui.QPixmap() 
        param["DbConnector"]=self.DbConnector        
        self.editWindow=EditItem.EditItemHandler(param, 'Add')
        self.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.getItems)
        self.editWindow.window.show()
        
    def editItem(self):
        Items=self.ItemTable.selectedItems()
        if len(Items)==0:
            message=QMessageBox()
            message.setText(u"Объект не выбран")
            message.exec_()
            return
        param={}
        param["itemId"]=int(Items[0].text())
        param["itemName"]=Items[1].text()
        param["itemPrice"]=Items[2].text()
        param["itemIcon"]=self.form.window.ibl_ItemIcon.pixmap()
        param["DbConnector"]=self.DbConnector
        self.editWindow=EditItem.EditItemHandler(param, 'Edit')
        self.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.getItems)
        self.editWindow.window.show()  