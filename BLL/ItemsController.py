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
        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
            
        except:
            print ('DataBase is NOT connected')
            self.errWindow=Errors(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
            
        cur.execute('SELECT idItem, itemName, ItemPrice from Items')
        result = cur.fetchall()
        conn.close()
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
            message=QMessageBox()
            message.setText(u"Объект не выбран")
            message.exec_()
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
                    
    def getIconById(self, idItem):
        conn=self.DbConnector.getConnection()
        cur=conn.cursor()
        cur.execute('SELECT ItemIcon from Items where idItem={}'.format(idItem))
        result=cur.fetchone()[0]
        qpixmap=QtGui.QPixmap()
        if result is not None:
            picBytes = base64.b64decode(result)
            qpixmap.loadFromData(picBytes)
        return qpixmap



        
 
        
        