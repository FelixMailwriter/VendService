# -*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QObject, QMessageBox 
from DAL.DBConnector import DbConnector
import base64
import EditItem
import Errors

class ItemsController(QObject):
    
    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.errWindow=Errors.Errors("")
        self.editWindow=None
        self.form.window.btn_AddItem.clicked.connect(self.addItem)
        self.form.window.btn_EditItem.clicked.connect(self.editItem)
        self.form.window.ItemTable.cellClicked.connect(self.refreshIcon)
         
               
        self.getItems()
        
    def getItems(self):
        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
        except:
            print ('DataBase is NOT connected')
            self.errWindow.setMessageText(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
            return
            
        cur.execute('SELECT idItem, itemName, ItemPrice from Items')
        result = cur.fetchall()
        conn.close()
        self.form.fillItemsTable(result)

    def addItem(self):
        param={}
        param["itemId"]=0
        param["itemName"]=""
        param["itemPrice"]="0"
        param["itemIcon"]=QtGui.QPixmap() 
        param["DbConnector"]=self.DbConnector
        self.editWindow=EditItem.EditItemHandler(param, 'Add')
        self.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.getItems)
        self.editWindow.window.show()
            
    def editItem(self):
        Items=self.form.getCurrentItems()
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
                    
    def refreshIcon(self, idItem):
        Items=self.form.window.ItemTable.selectedItems()
        idItem=int(Items[0].text())
        conn=self.DbConnector.getConnection()
        cur=conn.cursor()
        cur.execute('SELECT ItemIcon from Items where idItem={}'.format(idItem))
        result=cur.fetchone()[0]
        picBytes = base64.b64decode(result)
        qpixmap=QtGui.QPixmap()
        qpixmap.loadFromData(picBytes)
        self.form.setIcon(qpixmap)



        
 
        
        