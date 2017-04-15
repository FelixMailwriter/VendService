# -*- coding:utf-8 -*-

import os
from PyQt4.Qt import QObject, QFileDialog, QMessageBox, QByteArray, QBuffer
from PyQt4 import QtCore, QtGui, uic
import base64
import Errors

class EditItemHandler(QObject):
    
    def __init__(self, param, typeOperation):
        QObject.__init__(self)
        
        self.DbConnector=param["DbConnector"]
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
        self.checkPrice()
        self.window.lbl_Icon.setPixmap(self.itemIcon)
        
        self.window.btn_addPath.clicked.connect(self.loadIcon)
        self.window.btn_Save.clicked.connect(self.save)
        self.connect(self.window.le_ItemPrice, QtCore.SIGNAL("editingFinished()"),self.checkPrice)
        self.connect(self.window.btn_Close, QtCore.SIGNAL("clicked()"), self.window.close) 

        
    def addItem(self, itemIcon, **params):
        
        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
            picbyte=base64.b64encode(itemIcon)
            query='''Insert into vending.Items (ItemName, ItemPrice, ItemIcon) values ('%s', %d, '%s')''' %(self.itemName, self.itemPrice, picbyte)
            cur.execute(query)
            
            if cur.lastrowid:
                message=QMessageBox()
                message.setText(u"Данные добавлены")
                message.exec_()
            else:
                message=QMessageBox()
                message.setText(u"Ошибка добавления данных")
                message.exec_()
        
            conn.commit()
            
        except Errors as error:
            print (error)
        
        finally:
            cur.close()
            conn.close()
                    
    def editItem (self, icon):

        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
            picbyte=base64.b64encode(icon)
            query='''Update vending.Items SET ItemName='%s', ItemPrice=%d, ItemIcon='%s' WHERE idItem=%d''' %(self.itemName, self.itemPrice, self.picbyte, self.itemId)
            cur.execute(query)
       
            conn.commit()
            
        except Errors as error:
            print (error)
            
        finally:
            cur.close()
            conn.close()
        
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
        self.window.btn_Save.setEnabled(flag)
        
        
    def save(self):
        self.checkPrice
        #self.window.btn_Save.setEnabled(True)
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
            self.addItem(self.itemIcon)
        elif self.typeOperation=='Edit':
            self.editItem() 
        self.window.close()
        self.emit(QtCore.SIGNAL("RefreshItemTable"))
        
          