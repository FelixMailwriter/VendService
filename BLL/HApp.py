# -*- coding:utf-8 -*-

import os
from PyQt4 import QtCore, uic, QtGui 
from PyQt4.Qt import QObject, QFont, QHeaderView, QComboBox, QItemDelegate,\
    QMessageBox
from BLL.ItemsController import ItemsController
from Magazines import MagazinesController
from Report import ReportController
from Errors import Errors


class HApp(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.form=MainWindow()
        self.form.window.show()
        
class MainWindow(QObject):
        
    def __init__(self):
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/mainForm.ui")
        
        self.window=uic.loadUi(path)
        self.ItemTable=self.window.ItemTable
        self.MagazinsTable=self.window.tblw_Magazines 
              
        # Создаем контроллеры
        self.ItemsController=ItemsController(self)
        self.MagazinesController=MagazinesController(self)
        self.ReportController=ReportController(self)

        #Прописываем события кнопок для предметов        
        self.window.btn_AddItem.clicked.connect(self.addItem)
        self.window.btn_EditItem.clicked.connect(self.editItem)
        self.window.btn_DeleteItem.clicked.connect(self.deleteItem)
        self.window.ItemTable.cellClicked.connect(self.refreshIcon)
        
        #Прописываем события кнопок для магазинов
        self.window.btn_AddMag.clicked.connect(self.addMagazin)
        self.window.btn_DelMag.clicked.connect(self.delMagazin)
        self.window.btn_MagSave.clicked.connect(self.saveMagazins)
        
        #Подключаемся к событию окончания добавления и редактирования предмета
        #self.connect(self.ItemsController.editWindow, QtCore.SIGNAL("RefreshItemTable"), self.fillItemsTable)
        
        self.ItemsList=self.MagazinesController.getItemsList() #Список имеющихся предметов для выпадающего списка
        
        self.setUpTables()
        
    def setUpTables(self):
        rowsFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.MagazinsTable.setFont(rowsFont)
        headerFont=QFont('Lucida',12, QtGui.QFont.Bold)
        # Setting Items table
        self.ItemTable.setFont(rowsFont)
        self.ItemTable.horizontalHeader().setFont(headerFont) 
        self.ItemTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.ItemTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        self.ItemTable.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
        self.ItemTable.verticalHeader().hide()
        self.fillItemsTable()
         
        # Setting Magazins table       
        self.MagazinsTable.horizontalHeader().setFont(headerFont) 
        self.MagazinsTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.MagazinsTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        self.MagazinsTable.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
        self.MagazinsTable.horizontalHeader().setResizeMode(3,QHeaderView.Stretch)
        self.MagazinsTable.verticalHeader().hide()
        self.fillMagazinsTable()
          
    def fillItemsTable(self):#, rows):
        rows=self.ItemsController.getItems()
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
            
    def setIcon(self, qpixmap):
        self.window.ibl_ItemIcon.setPixmap(qpixmap)     
        
                
#------------------------------------------------------------
# Items
    def addItem(self):
        self.ItemsController.addItem()
        
    def editItem(self):
        selectedRow=self.ItemTable.selectedItems()
        self.ItemsController.editItem(selectedRow)       
    
    def deleteItem(self):
        selectedRow=self.ItemTable.selectedItems()
        self.ItemsController.deleteItem(selectedRow)
        
    def refreshIcon(self):
        Items=self.ItemTable.selectedItems()
        idItem=int(Items[0].text())
        qpixmap=self.ItemsController.getIconById(idItem)
        self.setIcon(qpixmap)

    #--------------------------------------------------------------
    # Magazins
    
    def fillMagazinsTable(self):
        rows=self.MagazinesController.getMagazinsItemsMap()
        if rows is None: return
        self.MagazinsTable.setItemDelegateForColumn(3, NonEditColumnDelegate())
        self.MagazinsTable.setRowCount(0)
        counter=0
        for row in rows:
            ItemIdMag=QtGui.QTableWidgetItem(str(str(row[0])))
            ItemIdMag.setTextAlignment(QtCore.Qt.AlignCenter)
            
            cmbx=QComboBox()
            cmbx.addItems(self.ItemsList)
            name=str(row[1])
            index=cmbx.findText(name)
            cmbx.setCurrentIndex(index)
            ItemItemQty=QtGui.QTableWidgetItem(str(row[2]))
            ItemItemQty.setTextAlignment(QtCore.Qt.AlignCenter)
            ItemIdItem=QtGui.QTableWidgetItem(str(row[3]))
            ItemIdItem.setTextAlignment(QtCore.Qt.AlignCenter)

            self.MagazinsTable.insertRow(counter)
            self.MagazinsTable.setItem(counter,0,ItemIdMag)
            self.MagazinsTable.setCellWidget(counter,1,cmbx)
            self.MagazinsTable.setItem(counter,2,ItemItemQty)
            self.MagazinsTable.setItem(counter,3,ItemIdItem)
            counter+=1 
            
    def addMagazin(self):
        rowCount=self.MagazinsTable.rowCount()
        self.MagazinsTable.insertRow(rowCount)
        cmbx=QComboBox()
        cmbx.addItems(self.ItemsList)
        cmbx.setCurrentIndex(-1)        
        self.MagazinsTable.setCellWidget(rowCount,1,cmbx)
        
    def delMagazin(self):
        currentRow=self.MagazinsTable.currentRow()
        self.MagazinsTable.removeRow(currentRow)            

    def saveMagazins(self):
        MagazinsMappingList=[]
        for i in range (0, self.MagazinsTable.rowCount()):
            row=[]
            for j in range (0, self.MagazinsTable.columnCount()):
                wgt=self.MagazinsTable.cellWidget(i,j)
                itemType=type(wgt)
                if str(itemType)=='<class \'PyQt4.QtGui.QComboBox\'>':
                    value=wgt.currentText()
                elif str(itemType)=='<type \'NoneType\'>': 
                    try:
                        value=self.MagazinsTable.item(i,j).text()
                    except:
                        value=0
                row.append(value)
            MagazinsMappingList.append(row)
            
        if self._checkCorrectMagazineTable(MagazinsMappingList): 
            return
        
        else: 
            self.MagazinesController._saveMagazinsMapping(MagazinsMappingList)
            
    def _checkCorrectMagazineTable(self, MagazinsMappingList):
        for i in range (0, len(MagazinsMappingList)-1):
            magazine=MagazinsMappingList[i]
            #Проверка заполнения номера магазина
            if magazine[0]==0:
                self.message=Errors(u'Не указан номер магазина')
                self.message.window.setWindowTitle(u'Ошибка')
                self.message.window.show()
                return True
            #Проверка числового значения в номере магазина
            if self._isNotNumber(magazine[0]):
                self.message=Errors(u'В поле номера магазина не числовое значение')
                self.message.window.setWindowTitle(u'Ошибка')
                self.message.window.show()
            #Проверка заполнения поля Количество
            if magazine[2]==0:
                self.message=Errors(u'Не заполнено поле "Количество"')
                self.message.window.setWindowTitle(u'Ошибка')
                self.message.window.show()
                return True
            #Проверка числового значения в поле Количество
            if self._isNotNumber(magazine[2]):
                self.message=Errors(u'В поле "Количество" не числовое значение')
                self.message.window.setWindowTitle(u'Ошибка')
                self.message.window.show() 
                return True                          
            #Проверка уникальности номера магазина
            for j in range (i+1, len(MagazinsMappingList)):
                if magazine[0]==MagazinsMappingList[j][0]:
                    self.message=Errors(u'Дублируются номера магазинов')
                    self.message.window.setWindowTitle(u'Ошибка')
                    self.message.window.show()
                    return True
        return False    
           
    def _isNotNumber(self, value):
        try:
            num= (int)(value)
        except:return True
        else: return False
            
       

class NonEditColumnDelegate(QItemDelegate):
    def createEditor(self, parent, options, index):
        return None
