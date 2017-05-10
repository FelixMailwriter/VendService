# -*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QObject, QStringList, QComboBox, QFont, QHeaderView, QItemDelegate
from DAL.DBConnector import DbConnector
import datetime
from Errors import Errors
import Printer.PrnDK350 as Printer
 

class MagazinesController(QObject):
    OPERATION_OUTCOME='-'
    OPERATION_INCOME='+'

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.ItemsList=self._getItemsList() #Список имеющихся предметов для выпадающего списка
        self.MagazinsTable=self.form.window.tblw_Magazines
        #Прописываем события кнопок для магазинов
        self.form.window.btn_AddMag.clicked.connect(self._addMagazin)
        self.form.window.btn_DelMag.clicked.connect(self._delMagazin)
        self.form.window.btn_MagSave.clicked.connect(self._saveMagazins)
        self.form.window.tblw_Magazines.cellClicked.connect(self._magTableCellClicked)
        self.form.window.btn_plus.clicked.connect(self._plusQty)
        self.form.window.btn_minus.clicked.connect(self._minusQty)

    def setUpMagazinsTable(self):
        rowsFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.MagazinsTable.setFont(rowsFont)
        headerFont=QFont('Lucida',12, QtGui.QFont.Bold)
        self.MagazinsTable.horizontalHeader().setFont(headerFont) 
        self.MagazinsTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.MagazinsTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        self.MagazinsTable.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
        self.MagazinsTable.horizontalHeader().setResizeMode(3,QHeaderView.Stretch)
        self.MagazinsTable.verticalHeader().hide()
        self._fillMagazinsTable()
        
    @QtCore.pyqtSlot(name="fillMagazinsTable")
    def _fillMagazinsTable(self):
        self.ItemsList=self._getItemsList() #Список имеющихся предметов для выпадающего списка
        rows=self.DbConnector.getMagazinsItemsMap()
        if rows is None or len(rows)==0: 
            return
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
  
    def _addMagazin(self):
        rowCount=self.MagazinsTable.rowCount()
        self.MagazinsTable.insertRow(rowCount)

        ItemItemQty=QtGui.QTableWidgetItem()
        ItemItemQty.setTextAlignment(QtCore.Qt.AlignCenter)
        self.MagazinsTable.setItem(rowCount,0,ItemItemQty)        
        
        cmbx=QComboBox()
        cmbx.addItems(self.ItemsList)
        cmbx.setCurrentIndex(-1)        
        self.MagazinsTable.setCellWidget(rowCount,1,cmbx)
        
        ItemItemQty=QtGui.QTableWidgetItem('0')
        ItemItemQty.setTextAlignment(QtCore.Qt.AlignCenter)
        self.MagazinsTable.setItem(rowCount,2,ItemItemQty)
        
    def _delMagazin(self):
        currentRow=self.MagazinsTable.currentRow()
        self.MagazinsTable.removeRow(currentRow)            

    def _saveMagazins(self):
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

        self._saveMagazinsMapping(MagazinsMappingList)
                     
    def _checkCorrectMagazineTable(self, MagazinsMappingList):
        for i in range (0, len(MagazinsMappingList)):
            magazine=MagazinsMappingList[i]
            #Проверка заполнения номера магазина
            if magazine[0]==0:
                self._showMessage(u'Ошибка', u'Не указан номер магазина')
                return True
            #Проверка числового значения в номере магазина
            if self._isNotNumber(magazine[0]):
                self._showMessage(u'Ошибка', u'В поле номера магазина не числовое значение')
                return True
            #Проверка заполнения поля Количество
            if magazine[2]=='0':
                self._showMessage(u'Ошибка', u'Не заполнено поле "Количество"')
                return True
            #Проверка числового значения в поле Количество
            if self._isNotNumber(magazine[2]):
                self._showMessage(u'Ошибка', u'В поле "Количество" не числовое значение')
                return True                          
            #Проверка уникальности номера магазина
            for j in range (i+1, len(MagazinsMappingList)):
                if magazine[0]==MagazinsMappingList[j][0]:
                    self._showMessage(u'Ошибка', u'Дублируются номера магазинов')
                    return True
        return False    
           
    def _isNotNumber(self, value):
        try:
            num= (int)(value)
        except:return True
        else: return False
            
    def _magTableCellClicked(self, row, column):
        item=self.MagazinsTable.item(row, 0)
        if item is None: return
        magNum=item.text()        
        self.form.window.lbl_magNumber.setText(magNum) 
    
    def _plusQty(self):
        qty=self._getQtyToChange()
        row=self.MagazinsTable.currentRow()
        if row == -1: return
        oldValue=int(self.MagazinsTable.item(row, 2).text())
        newValue=oldValue+qty
        self.MagazinsTable.item(row,2).setText(str(newValue))

    def _minusQty(self):
        qty=self._getQtyToChange()
        row=self.MagazinsTable.currentRow()
        if row == -1: return
        oldValue=int(self.MagazinsTable.item(row, 2).text())
        newValue=oldValue-qty
        if newValue<=0:
            self._showMessage(u'Ошибка', u'Удаляемое количество предметов больше имеющегося')
            return            
        self.MagazinsTable.item(row,2).setText(str(newValue))         
    
    def _getQtyToChange(self):
        value=self.window.le_qty.text()
        try:
            qty=(int)(value)
        except:
            self._showMessage(u'Ошибка', u'В поле "Количество" не числовое значение')
            return 0                        
        else:
            return qty
                
    def _getItemsList(self):
        result=self.DbConnector.getItems(False)    
        listItems=QStringList()
        if result is None or len(result)==0: 
            return listItems
        for element in result:
            listItems.append(element[1])                 
        return listItems    
           
    def _saveMagazinsMapping(self, magazinesMap):
        #Дописываем в таблицу предметов их id
        self._addIdToMagazinesMap(magazinesMap)
        #Записываем в БД приход/расход предметов
        result=self._inOutCommingItems(magazinesMap)
        #Очищаем таблицу предметов
        if not self._dropMagazinesTable(): return
        #Записываем в таблицу предметов новые значения
        for magazin in magazinesMap:
            param={}
            param["magazineNumber"]=(int)(magazin[0])
            param["itemName"]=magazin[1]
            param ["itemQty"]=int(magazin[2])
            param ["itemId"]=magazin[3]

            self._insertMagazine(param)
            
    def _addIdToMagazinesMap(self, magazinesMap):
        for row in magazinesMap:
            itemName=row[1]
            item=self.DbConnector.getIdItemByName(itemName, False)
            if item is not None and len(item)>0:
                itemId=item[0][0]
                row.append(itemId)
            
    def _inOutCommingItems(self, magazinesMap):
        ItemsInOldTable=self.DbConnector.getQtyOfItemsByType()
        ItemsInNewTable=self._groupMagazinesMapTable(magazinesMap)
        ItemMovementTable=self._getItemMovementTable(ItemsInOldTable, ItemsInNewTable)
        result=self.DbConnector.getMaxMovementId()[0]
        if result is None:
            result=0    
        idRecharge=result+1
        for itemMovement in ItemMovementTable:
            idItem=itemMovement[0]
            date=datetime.datetime.now()
            OperationType=itemMovement[1]
            itemQty=itemMovement[2]
            result=self.DbConnector.addMovement(idRecharge, idItem, date, OperationType, itemQty)
              
        #Печатаем отчеты
        if len(ItemMovementTable)==0:
            #печатаем отчет о загрузке магазинов
            magazinesLoadReport=self._makeMagazinesLoadReport()
            self._printReport(magazinesLoadReport, 'NotFisk')
        else:    
            #печатаем отчет о перезарядке
            printRechargeReport=self._makeRechargeReport(ItemsInOldTable, ItemsInNewTable)
            self._printReport(printRechargeReport, 'NotFisk')
        return result

    def _groupMagazinesMapTable(self,magazinesMap):
        #Функция группирует предметы, указанные в списке магазинов, суммируя их по видам
        ItemsId=[]
        qty=[]
        ItemsName=[]
        for i in range(0, len(magazinesMap)):
            idItem=int(magazinesMap[i][3])
            itemQty=int(magazinesMap[i][2])
            itemName=str(magazinesMap[i][1])
            if idItem in ItemsId: 
                continue            
            if len(magazinesMap)==1:
                ItemsId.append(idItem)
                qty.append(itemQty)
                ItemsName.append(itemName)
                break

            for j in range (i+1, len(magazinesMap)):
                if idItem==int(magazinesMap[j][3]):
                    itemQty+=int(magazinesMap[j][2])
            ItemsId.append(idItem)
            qty.append(itemQty)
            ItemsName.append(itemName)
        result=zip(ItemsId,qty,ItemsName)
        return result        

    def _getItemMovementTable(self, ItemsInOldTable, ItemsInNewTable):
        #Функция формирует список движений предметов: приход/расход
        itemsMovementTable=[]
        #Перебираем предметы в новой таблице (заполненной в интерфейсе)
        for newItem in ItemsInNewTable:
            newItemId=newItem[0]
            oldItemQty=0
            #Сравниваем предмет из новой таблице со списком предметов в таблице, полученной из БД
            for oldItem in ItemsInOldTable:
                oldItemId=oldItem[0]
                #Если предметы совпали, то получаем количество предметов из базы (старое, до обновления)
                if newItemId==oldItemId:
                    oldItemQty=oldItem[1]
            #Получаем разницу количества предметов по сравнению со старым (из БД) значением 
            qty=newItem[1]-oldItemQty
            if qty==0:
                continue
            #Создаем движение
            itemMovement=[]
            #Если новых предметов стало больше, то это - приход
            if qty>0:
                itemMovement.append(int(newItemId))
                itemMovement.append(self.OPERATION_INCOME)
                itemMovement.append(qty)
            #Если новых предметов стало меньше, то это - расход
            elif qty<0:
                itemMovement.append(int(newItemId))
                itemMovement.append(self.OPERATION_OUTCOME)
                itemMovement.append(qty)
            itemsMovementTable.append(itemMovement)
    
        #Перебираем предметы которые были в старой (из БД) таблице и выбираем только те, которых нет в 
        #новой таблице, заполненной в интерфейсе, т.е. их полностью выгрузили из магазинов. Это - расход
        for oldItem in ItemsInOldTable:
            oldItemId=oldItem[0]
            oldItemQty=oldItem[1]
            itemExists=False
            for newItem in ItemsInNewTable:
                newItemId=newItem[0]
                if oldItemId==newItemId:
                    itemExists=True
                    break
            if not itemExists:
                itemMovement=[]
                itemMovement.append(int(oldItemId))
                itemMovement.append(self.OPERATION_OUTCOME)
                itemMovement.append(oldItemQty)
                itemsMovementTable.append(itemMovement) 
        
        return itemsMovementTable    
  
    def _insertMagazine(self, param):
        #Получаем Id предмета по его имени
        result=self.DbConnector.getIdItemByName(param["itemName"],False)
        #Прописываем предмет в магазине
        if result is not None:
            itemId=result[0][0]
            sucsess=self.DbConnector.addMagazin(param["magazineNumber"], itemId, param["itemQty"])
            if sucsess:
                self._showMessage(u'Результат операции', u"Данные записаны")
            else: 
                self._showMessage(u'Результат операции', u"Ошибка записи в базу данных")           
        else:
            self._showMessage(u'Ошибка', u"Ошибка выборки данных из базы")
    
    def _dropMagazinesTable(self):
        result=self.DbConnector.dropMagazinesTable()
        return result 
    
    def _makeRechargeReport(self, ItemsInOldTable, ItemsInNewTable):
        context=[]
        itemMovementTable=self.DbConnector.getMovements()
        if len(itemMovementTable)==0 or itemMovementTable is None:
            return
        context.append(dict(Text=''))
        context.append(dict(Text='Report: %s' %(str(itemMovementTable[0][0]))))
        context.append(dict(Text='Date: %s' %(str(itemMovementTable[0][2]))))
            
        context.append(dict(Text='--------------------------------------'))
        context.append(dict(Text=''))
        context.append(dict(Text='{:^35}'.format('Begin:')))
        for item in ItemsInOldTable:
            row='{:<35}{:>3}'.format(str(item[2]), str(item[1]))
            context.append(dict(Text=row))
            
        context.append(dict(Text=''))
        context.append(dict(Text='--------------------------------------'))
        
        if len(itemMovementTable)==0:
            return 
                        
        context.append(dict(Text='{:^35}'.format('Movements:')))
        for item in itemMovementTable:
            if item[3]==self.OPERATION_INCOME:
                sign='+'
            else:
                sign='-'
            row='{:<34}{}{:>3}'.format(str(item[1]), sign, str(abs(item[4])))
            context.append(dict(Text=row))
        
        context.append(dict(Text=''))
        context.append(dict(Text='--------------------------------------')) 
        
        context.append(dict(Text='{:^35}'.format('Rest:')))      
        for item in ItemsInNewTable:
            row='{:<35}{:>3}'.format(str(item[2]), str(item[1]))
            context.append(dict(Text=row))

        context.append(dict(Text=''))
        context.append(dict(Text=''))
        context.append(dict(Text='--------------------------------------'))
        
        for s in context:
            st=s['Text']
            print st
                    
        return context
                    
    def _makeMagazinesLoadReport(self):
        result=self.DbConnector.getMagazinLoadTable()
        context=[]
        context.append(dict(Text=''))
        context.append(dict(Text='{:^35}'.format('Magazines load')))  
        context.append(dict(Text='{:^35}'.format('Date: %s' %(str(datetime.datetime.now())))))
        context.append(dict(Text='------------'))
        context.append(dict(Text=''))               
        for row in result:
            rowStr='{:<35}{:>3}'.format(str(row[0])+'.'+ str(row[1]), str(row[2]))
            context.append(dict(Text=rowStr))
        context.append(dict(Text='')) 
        context.append(dict(Text='------------'))
        
        for s in context:
            st=s['Text']
            print st        
        
        return context
                         
    def _printReport(self, context, checkType):
        try:
            printer=Printer.Printer()
            logMessages=printer.checkStatus()
            self.DbConnector.writeLog(logMessages)
            printer.run(context, checkType)
        except Printer.PrinterHardwareException as e:
            self.emit(QtCore.SIGNAL('Printer is not ready'), e.value)

    def _showMessage(self, header, message):
        self.message=Errors(message)
        self.message.window.setWindowTitle(header)
        self.message.setParent(self)
        self.message.window.show() 
    
class NonEditColumnDelegate(QItemDelegate):
    def createEditor(self, parent, options, index):
        return None
    
                  
        