# -*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QObject, QMessageBox 
import base64
from DAL.DBConnector import DbConnector
import EditItem
from Errors import Errors

class ItemsController(QObject):
    
    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.editWindow=None

        
    def getItems(self):
        query='SELECT idItem, itemName, ItemPrice from Items'
        result = self.DbConnector.getDataFromDb(query)
        return result

    def addItem(self):
        param={}
        param["itemId"]=0
        param["itemName"]=""
        param["itemPrice"]="0"
        param["itemIcon"]=QtGui.QPixmap() 
        param["DbConnector"]=self.DbConnector
        self.editWindow=EditItem.EditItemHandler(param, 'Add')
        self.form.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.form.fillItemsTable)
        self.editWindow.window.show()
            
    def editItem(self, selectedRow):
        if len(selectedRow)==0:
            self.message=Errors(u"Объект не выбран")
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()
            return
        param={}
        param["itemId"]=int(selectedRow[0].text())
        param["itemName"]=selectedRow[1].text()
        param["itemPrice"]=selectedRow[2].text()
        param["itemIcon"]=self.form.window.ibl_ItemIcon.pixmap()
        param["DbConnector"]=self.DbConnector
        self.editWindow=EditItem.EditItemHandler(param, 'Edit')
        self.form.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.form.fillItemsTable)
        self.editWindow.window.show() 
        
    def deleteItem(self, selectedRow):
        if len(selectedRow)==0:
            self.message=Errors(u"Объект не выбран")
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()
            return
        idItem=int(selectedRow[0].text())
        MagazinesWithItems=self._getMagazinesContainItem(idItem)
        if len(MagazinesWithItems)!=0:
            magList=''
            for magazine in MagazinesWithItems:
                magList+=str(magazine[0])+', '
            magList=magList[:-2]
            msg=u'Удаление невозможно. Предмет загружен в магазин(ы) '+magList
            self.message=Errors(msg)
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()
            return
        query='Delete from Items where idItem=%d' %(idItem)
        self.DbConnector.deleteDataFromTable(query)
        self.form.fillItemsTable()
        
            
                               
    def getIconById(self, idItem):
        query='SELECT ItemIcon from Items where idItem={}'.format(idItem)
        result=self.DbConnector.getDataFromDb(query)[0][0]

        qpixmap=QtGui.QPixmap()
        if result is not None:
            picBytes = base64.b64decode(result)
            qpixmap.loadFromData(picBytes)
        return qpixmap

    def _getMagazinesContainItem(self, idItem):
        query= ('select idMagazins, ItemQty, itemId from Magazins'+
        ' where Magazins.ItemId=%d') %(idItem)
        result=self.DbConnector.getDataFromDb(query)
        return result
        

        
 
        
        