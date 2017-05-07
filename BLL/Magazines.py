# -*- coding:utf-8 -*-

from PyQt4 import QtCore
from PyQt4.Qt import QObject, QStringList
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
        self.MagazinsTable=self.form.window.tblw_Magazines
        self.getItemsList()
        
    def getItemsList(self):
        query='select ItemName from Items order by ItemName'
        result=self.DbConnector.getDataFromDb(query)    
        listItems=QStringList()
        if result is None: return listItems
        for element in result:
            listItems.append(element[0])                 
        return listItems    

    def getMagazinsItemsMap(self):
        query= ('select idMagazins, itemName, ItemQty, Items.idItem from Magazins,'+
        ' Items where Magazins.ItemId=Items.idItem')
        result=self.DbConnector.getDataFromDb(query)
        return result
               
    def saveMagazinsMapping(self, magazinesMap):
        #Дописываем в таблицу предметов их id
        self._addIdToMagazinesMap(magazinesMap)
        #Записываем в БД приход/расход предметов
        result=self._inOutCommingItems(magazinesMap)
        if not result:
            self.message=Errors(u"Ошибка записи движений предметов")
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()             
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
            itemId=self._getItemIdByName(itemName)
            row.append(itemId)
            
    def _inOutCommingItems(self, magazinesMap):
        result=True
        query='Select Magazins.ItemId, sum(Magazins.ItemQTY), Items.ItemName from Magazins, Items ' +\
                'where Magazins.ItemId=Items.idItem ' +\
                'group by ItemId '+\
                'order by Items.itemName'

        ItemsInOldTable=self.DbConnector.getDataFromDb(query)
        ItemsInNewTable=self._groupMagazinesMapTable(magazinesMap)
        ItemMovementTable=self._getItemMovementTable(ItemsInOldTable, ItemsInNewTable)
        query='Select max(IdMovement) from ItemsMovements'
        result=self.DbConnector.getDataFromDb(query, 'one')[0]
        if result is None:
            result=0
            
        idRecharge=result+1
        for itemMovement in ItemMovementTable:
            idItem=itemMovement[0]
            date=datetime.datetime.now()
            OperationType=itemMovement[1]
            itemQty=itemMovement[2]
            query='Insert into ItemsMovements (IdMovement, idItem, OperationDate, OperationType, qty) '+\
                 'VALUES (%d, %d, \'%s\', \'%s\', %d)' %(idRecharge, idItem, date, OperationType, itemQty)
            result=self.DbConnector.insertDataToDB(query)
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
            #Сравниваем предмет из новой таблице со списком предметов в таблице, полученной изБД
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
        
        return itemsMovementTable    
  
    def _insertMagazine(self, param):
        #Получаем Id предмета по его имени
        query='Select idItem from Items where ItemName Like \'%s\'' %(param["itemName"])
        result=self.DbConnector.getDataFromDb(query)
        #Прописываем предмет в магазине
        if result is not None:
            itemId=result[0][0]
            query='Insert into Magazins (idMagazins, ItemId, ItemQTY) values (%d, %d, %d)' %\
                (param["magazineNumber"], itemId, param["itemQty"])
            sucsess=self.DbConnector.insertDataToDB(query)
            if sucsess:
                self.message=Errors(u"Данные записаны")
                self.message.window.setWindowTitle(u'Результат операции')
                self.message.window.show()
            else:            
                self.message=Errors(u"Ошибка записи в базу данных")
                self.message.window.setWindowTitle(u'Результат операции')
                self.message.window.show()                    
        else:
            self.message=Errors(u"Ошибка выборки данных из базы")
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()                                  
    
    def _dropMagazinesTable(self):
        query='Delete from Magazins'
        return self.DbConnector.deleteDataFromTable(query) 
    
    
    def _getItemIdByName(self, itemName):
        query='Select idItem from Items Where ItemName like \'%s\'' %(itemName)
        result=self.DbConnector.getDataFromDb(query)
        return result[0][0]
            
    def _makeRechargeReport(self, ItemsInOldTable, ItemsInNewTable):
        context=[]
        query='select IM.IdMovement, Items.itemName, IM.OperationDate, IM.OperationType, '+\
                'IM.qty from ItemsMovements as IM, Items '+\
                'where IM.IdMovement=(select max(IdMovement) from ItemsMovements) '+\
                'and IM.idItem=Items.idItem '+\
                'order by Items.itemName'
        itemMovementTable=self.DbConnector.getDataFromDb(query)
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
        query='select M.idMagazins, I.ItemName, M.ItemQTY from Magazins as M, Items as I '+\
                'where M.ItemId=I.idItem'
        result=self.DbConnector.getDataFromDb(query)
        
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

    
    
    
                  
        