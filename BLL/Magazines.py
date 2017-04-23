# -*- coding:utf-8 -*-

from PyQt4.Qt import QObject, QStringList
from DAL.DBConnector import DbConnector
from Errors import Errors
from BllEnums import ItemMoveOperationTypes 

class MagazinesController(QObject):

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
        #Записываем в БД приход/расход предметов
        self.inOutCommingItems(magazinesMap)
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
    
    def inOutCommingItems(self, magazinesMap):
        query='Select ItemId, sum(ItemQTY) from Magazins group by ItemId'
        ItemsInOldTable=self.DbConnector.getDataFromDb(query)
        ItemsInNewTable=self._getItemsNewTable(magazinesMap)
        ItemMovementTable=self._getItemMovementTable(ItemsInOldTable, ItemsInNewTable)
    
    def _getItemsNewTable(self,magazinesMap):
        ItemsId=[]
        qty=[]
        for i in range(0, len(magazinesMap)):
            idItem=magazinesMap[i][3]
            itemQty=int(magazinesMap[i][2])
            if idItem in ItemsId: 
                continue            
            if len(magazinesMap)==1:
                ItemsId.append(magazinesMap[0][3])
                qty.append(int(magazinesMap[0][2]))
                break

            for j in range (i+1, len(magazinesMap)):
                if idItem==magazinesMap[j][3]:
                    itemQty+=int(magazinesMap[j][2])
            ItemsId.append(idItem)
            qty.append(itemQty)
        result=zip(ItemsId,qty)
        return result
            
    def _getItemMovementTable(self, ItemsInOldTable, ItemsInNewTable):
        itemsMovementTable=[]
        for newItem in ItemsInNewTable:
            newItemId=newItem[0]
            oldItemQty=0
            for oldItem in ItemsInOldTable:
                oldItemId=oldItem[0]
                if newItemId==oldItemId:
                    oldItemQty=oldItem[1]
            qty=newItem[1]-oldItemQty
            itemMovement=[]
            if qty>0:
                itemMovement.append(newItemId)
                itemMovement.append(ItemMoveOperationTypes.Income)
                itemMovement.append(qty)
            elif qty<0:
                itemMovement.append(newItemId)
                itemMovement.append(ItemMoveOperationTypes.OutCome)
                itemMovement.append(-qty)
            itemsMovementTable.append(itemMovement) 
        
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
                itemMovement.append(oldItemId)
                itemMovement.append(ItemMoveOperationTypes.OutCome)
                itemMovement.append(oldItemQty) 
        
        return itemsMovementTable                  
        
        
            
         
        