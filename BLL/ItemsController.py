# -*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QObject, QFont, QHeaderView
import base64
from DAL.DBConnector import DbConnector
import EditItem
from Errors import Errors

class ItemsController(QObject):
    
    ItemDeleted=QtCore.pyqtSignal()
    
    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.editWindow=None
        self.ItemTable=self.form.window.ItemTable

        #Прописываем события кнопок для предметов        
        self.form.window.btn_AddItem.clicked.connect(self._addItem)
        self.form.window.btn_EditItem.clicked.connect(self._editItem)
        self.form.window.btn_DeleteItem.clicked.connect(self._deleteItem)
        self.form.window.ItemTable.cellClicked.connect(self._refreshIcon)
    
    def setUpItemsTable(self):
        rowsFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.ItemTable.setFont(rowsFont)
        headerFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.ItemTable.setFont(rowsFont)
        self.ItemTable.horizontalHeader().setFont(headerFont) 
        self.ItemTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.ItemTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        self.ItemTable.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
        self.ItemTable.verticalHeader().hide()
        self._fillItemsTable()
        
    def _fillItemsTable(self):
        rows=self._getItems(False)
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
    
    def _getItems(self, hidden):
        return self.DbConnector.getItems(hidden)

    def _addItem(self):
        param={}
        param["itemId"]=0
        param["itemName"]=""
        param["itemPrice"]="0"
        param["itemIcon"]=QtGui.QPixmap() 
        self.editWindow=EditItem.EditItemHandler(param, 'Add')
        self.connect(self.editWindow, QtCore.SIGNAL('RefreshItemTable'), self.form.setUpTables)
        self.editWindow.window.show()
            
    def _editItem(self):
        selectedRow=self.form.window.ItemTable.selectedItems()
        if len(selectedRow)==0:
            message=u"Объект не выбран"
            self._showMessage(u'Ошибка', message)
            return
        param={}
        param["itemId"]=int(selectedRow[0].text())
        param["itemName"]=selectedRow[1].text()
        param["itemPrice"]=selectedRow[2].text()
        param["itemIcon"]=self.form.window.ibl_ItemIcon.pixmap()
        self.editWindow=EditItem.EditItemHandler(param, 'Edit')
        self.connect(self.editWindow, QtCore.SIGNAL('RefreshItemTable'), self.form.setUpTables)
        self.editWindow.window.show() 
        
    def _deleteItem(self):
        selectedRow=self.form.window.ItemTable.selectedItems()
        if len(selectedRow)==0:
            message=u"Объект не выбран"
            self._showMessage(u'Ошибка', message)
            return
        idItem=int(selectedRow[0].text())
        MagazinesWithItems=self.DbConnector.getMagazinesContainItem(idItem)
        if len(MagazinesWithItems)!=0:
            message=u'Удаление невозможно. Предмет загружен в магазин(ы): '+MagazinesWithItems
            self._showMessage(u'Ошибка', message)            
            return
        #Проверяем был ли предмет хотя бы раз продан
        sellsOfItem=self.DbConnector.sellsOfItem(idItem)
        if len(sellsOfItem)>0:
            #Предмет был продан - делаем его невидимым
            result=self.DbConnector.setItemHide(idItem, True)
            if not result:
                message=u'Ошибка базы данных. Предмет не удален.'
                self._showMessage(u'Ошибка', message)
                return                
        else:
            #Удаляем предмет
            result=self.DbConnector.deleteItem(idItem)
            if result:
                message=u'Предмет удален.'
                self._showMessage(u'Операция успешна', message)
        self._fillItemsTable()
        self.ItemDeleted.emit()
              
    def _refreshIcon(self):
        Items=self.form.window.ItemTable.selectedItems()
        idItem=int(Items[0].text())
        qpixmap=self._getIconById(idItem)
        self._setIcon(qpixmap)
                                       
    def _getIconById(self, idItem):
        result=self.DbConnector.getIconById(idItem)[0]
        qpixmap=QtGui.QPixmap()
        if result is not None:
            picBytes = base64.b64decode(result)
            qpixmap.loadFromData(picBytes)
        return qpixmap
    
    def _setIcon(self, qpixmap):
        self.form.window.ibl_ItemIcon.setPixmap(qpixmap)
  
    def _showMessage(self, header, message):
        self.message=Errors(message)
        self.message.window.setWindowTitle(header)
        self.message.setParent(self)
        self.message.window.show() 
        
 
        
        