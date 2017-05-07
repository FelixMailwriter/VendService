# -*- coding:utf-8 -*-

import os
from PyQt4.Qt import QObject, QFileDialog, QByteArray, QBuffer
from PyQt4 import QtCore, QtGui, uic
import base64
from Errors import Errors
from DAL.DBConnector import DbConnector

class EditItemHandler(QObject):
    
    def __init__(self, param, typeOperation):
        QObject.__init__(self)
        
        self.DbConnector=DbConnector()
        self.typeOperation=typeOperation
        self.itemId=param["itemId"]
        self.itemName=param["itemName"]
        if param["itemPrice"]=="0":
            self.itemPrice=0
        else:
            self.itemPrice=param["itemPrice"]
        self.itemIcon=param["itemIcon"]
        path=os.path.abspath("UI/UIForms/EditItem.ui")
        self.window=uic.loadUi(path)
        self.window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.window.setWindowModality(2)
        self.window.le_ItemName.setText("{}".format(self.itemName))
        if self.typeOperation=='Edit':
            self.window.le_ItemName.setEnabled(False) 
        self.window.le_ItemPrice.setText("{}".format(self.itemPrice))
        self.checkPrice()
        self.window.lbl_Icon.setPixmap(self.itemIcon)
        
        self.window.btn_addPath.clicked.connect(self.loadIcon)
        self.window.btn_Save.clicked.connect(self._save)
        self.connect(self.window.le_ItemPrice, QtCore.SIGNAL("editingFinished()"),self.checkPrice)
        self.connect(self.window.btn_Close, QtCore.SIGNAL("clicked()"), self.window.close) 
       
    def addItem(self, itemIcon):
        picbyte=base64.b64encode(itemIcon)
        if self._checkNameExists(self.itemName):
            return
        result=self.DbConnector.addItem(self.itemName, self.itemPrice*100, picbyte, 0)    
        if result:
            message=u"Данные добавлены"
            self._showMessage(u'Операция успешна', message)
                    
    def editItem (self, itemIcon):
        picbyte=base64.b64encode(itemIcon)
        result=self.DbConnector.editItem(self.itemName, self.itemPrice*100, picbyte, 0, self.itemId)
        if result:
            message=u"Данные обновлены"
            self._showMessage(u'Операция успешна', message)
        else:
            message=u"Ошибка обновления"
            self._showMessage(u'Ошибка', message)                

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
            message=u"В поле Цена не числовое значение"
            self._showMessage(u'Ошибка', message)
        self.window.btn_Save.setEnabled(flag)
             
    def _save(self):
        self.checkPrice
        self.itemName=self.window.le_ItemName.text()
        if self.itemName=="" or self.itemPrice==0 or self.itemIcon is None:
            message=u"Не все данные указаны"
            self._showMessage(u'Ошибка', message)
            self.window.btn_Save.setEnabled(False)
            return
        blobImg=QByteArray()
        buff=QBuffer(blobImg)
        buff.open(QBuffer.WriteOnly)
        
        self.itemIcon.save(buff, "JPG")
        if self.typeOperation=='Add':
            self.addItem(blobImg)
        elif self.typeOperation=='Edit':
            self.editItem(blobImg) 
        self.window.close()
        self.emit(QtCore.SIGNAL("RefreshItemTable"))
    
    def _checkNameExists(self, itemName):
        query='Select idItem from Items where itemName like \'%s\'' %(itemName)
        result=self.DbConnector.getDataFromDb(query)
        if len(result)>0:
            message=u"Предмет с таким именем существует"
            self._showMessage(u'Ошибка', message)
            return True
        return False             
 
    def _showMessage(self, header, message):
        self.message=Errors(message)
        self.message.window.setWindowTitle(header)
        self.message.window.show()   
    
    
        
          