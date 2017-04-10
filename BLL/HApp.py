# -*- coding:utf-8 -*-

import os
import Errors
from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import QObject, QFileDialog, QMessageBox, QByteArray, QBuffer
from DAL.DBConnector import DbConnector
import base64

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


        
class ObjHandler(QObject):
    def __init__(self, window):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.window=window.window
        self.ItemTable=self.window.ItemTable
        self.ItemTable.cellClicked.connect(self.refreshIcon)
        self.window.btn_AddItem.clicked.connect(self.addItem)
        self.window.btn_EditItem.clicked.connect(self.editItem)
        self.errWindow=Errors.Errors("")
        
    def getItems(self):
        #self.ItemTable.clear()
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
        self.window.ibl_ItemIcon.setPixmap(qpixmap)

    def addItem(self):
        count=self.ItemTable.rowCount()+1
        self.ItemTable.insertRow(count)
        param={}
        param["itemId"]=0
        param["itemName"]=""
        param["itemPrice"]=""
        param["itemIcon"]=QtGui.QPixmap()         
        self.editWindow=EditItem(param, 'Add')
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
        param["itemIcon"]=self.window.ibl_ItemIcon.pixmap()
        self.editWindow=EditItem(param, 'Edit')
        self.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.getItems)
        self.editWindow.window.show()        
       
        
class EditItem(QObject):
    
    def __init__(self, param, typeOperation):
        QObject.__init__(self)
        
        self.typeOperation=typeOperation
        self.itemId=param["itemId"]
        self.itemName=param["itemName"]
        if param["itemPrice"]==0:
            self.itemPrice=0
        else:
            self.itemPrice=param["itemPrice"]
        self.itemIcon=param["itemIcon"]
        path=os.path.abspath("UI/UIForms/EditItem.ui")
        self.window=uic.loadUi(path)
        self.window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowModality(2)
        self.window.le_ItemName.setText("{}".format(self.itemName))
        self.window.le_ItemPrice.setText("{}".format(self.itemPrice))
        self.window.lbl_Icon.setPixmap(self.itemIcon)
        
        self.window.btn_addPath.clicked.connect(self.loadIcon)
        self.window.btn_Save.clicked.connect(self.save)
        self.connect(self.window.le_ItemPrice, QtCore.SIGNAL("editingFinished()"),self.checkPrice)
        self.connect(self.window.btn_Close, QtCore.SIGNAL("clicked()"), self.window.close) 
        
        self.DbConnector=DbConnector()
        
    def loadIcon(self):
        file, fd=QFileDialog.getOpenFileNameAndFilter(parent=self.window, filter="Images *.jpg (*.jpg)")
        self.window.le_ItemImgPath.setText(file)
        self.itemIcon=QtGui.QPixmap()
        self.itemIcon.load(file)
        self.window.lbl_Icon.setPixmap(self.itemIcon)
        
    def checkPrice(self):
        flag=True
        try:
            self.itemPrice=float(self.window.le_ItemPrice.text())
        except:
            flag=False
            message=QMessageBox()
            message.setText(u"В поле Цена не числовое значение")
            message.exec_()
        self.window.btn_Add.setEnabled(flag)
        
        
    def save(self):
        self.window.btn_Save.setEnabled(True)
        self.itemName=self.window.le_ItemName.text()
        if self.itemName=="" or self.itemPrice==0 or self.itemIcon is None:
            message=QMessageBox()
            message.setText(u"Не все данные указаны")
            message.exec_()
            self.window.btn_Add.setEnabled(False)
            return
        blobImg=QByteArray()
        buff=QBuffer(blobImg)
        buff.open(QBuffer.WriteOnly)
        
        self.itemIcon.save(buff, "JPG")
        if self.typeOperation=='Add':
            self.DbConnector.addItem(blobImg, ItemName=self.itemName, ItemPrice=self.itemPrice )
        elif self.typeOperation=='Edit':
            self.DbConnector.editItem(blobImg, ItemId=self.itemId, ItemName=self.itemName, ItemPrice=self.itemPrice) 
        self.window.close()
        self.emit(QtCore.SIGNAL("RefreshItemTable"))
            
        
        
        
        