# -*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QObject
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

        #Прописываем события кнопок для предметов        
        self.form.window.btn_AddItem.clicked.connect(self._addItem)
        self.form.window.btn_EditItem.clicked.connect(self._editItem)
        self.form.window.btn_DeleteItem.clicked.connect(self._deleteItem)
        self.form.window.ItemTable.cellClicked.connect(self._refreshIcon)
    
    # Items
    '''
    def _addItem(self):
        self.ItemsController.addItem()
        
    def _editItem(self):
        selectedRow=self.ItemTable.selectedItems()
        self.ItemsController.editItem(selectedRow)       
    
    def _deleteItem(self):
        selectedRow=self.ItemTable.selectedItems()
        self.ItemsController.deleteItem(selectedRow)
    '''    
    def _refreshIcon(self):
        Items=self.form.window.ItemTable.selectedItems()
        idItem=int(Items[0].text())
        qpixmap=self._getIconById(idItem)
        self.setIcon(qpixmap)
           
    def getItems(self):
        query='SELECT idItem, itemName, ItemPrice from Items'
        result = self.DbConnector.getDataFromDb(query)
        return result
    
    def _addItem(self):
        param={}
        param["itemId"]=0
        param["itemName"]=""
        param["itemPrice"]="0"
        param["itemIcon"]=QtGui.QPixmap() 
        #param["DbConnector"]=self.DbConnector
        self.editWindow=EditItem.EditItemHandler(param, 'Add')
        self.form.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.form.fillItemsTable)
        self.editWindow.window.show()
            
    def _editItem(self):
        selectedRow=self.form.window.ItemTable.selectedItems()
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
        #param["DbConnector"]=self.DbConnector
        self.editWindow=EditItem.EditItemHandler(param, 'Edit')
        self.form.connect(self.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.form.fillItemsTable)
        self.editWindow.window.show() 
        
    def _deleteItem(self, selectedRow):
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
        #Делаем предмет невидимым
        query=''
        query='Delete from Items where idItem=%d' %(idItem)
        self.DbConnector.deleteDataFromTable(query)
        self.form.fillItemsTable()            
                               
    def _getIconById(self, idItem):
        query='SELECT ItemIcon from Items where idItem={}'.format(idItem)
        result=self.DbConnector.getDataFromDb(query)[0][0]

        qpixmap=QtGui.QPixmap()
        if result is not None:
            picBytes = base64.b64decode(result)
            qpixmap.loadFromData(picBytes)
        return qpixmap
    
    def setIcon(self, qpixmap):
        self.form.window.ibl_ItemIcon.setPixmap(qpixmap)

    def _getMagazinesContainItem(self, idItem):
        query= ('select idMagazins, ItemQty, itemId from Magazins'+
        ' where Magazins.ItemId=%d') %(idItem)
        result=self.DbConnector.getDataFromDb(query)
        return result
        

        
 
        
        