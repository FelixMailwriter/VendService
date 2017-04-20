# -*- coding:utf-8 -*-

from PyQt4.Qt import QObject, QStringList
from DAL.DBConnector import DbConnector
from Errors import Errors

class MagazinesController(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.MagazinsTable=self.form.window.tblw_Magazines
        self.getItemsList()
        
    def getItemsList(self):
        query='select ItemName from Items order by ItemName'
        result=self._getDataFromDB(query)
            
        listItems=QStringList()
        if result is None: return listItems
        
        for element in result:
            listItems.append(element[0]) 
                        
        return listItems    

    def getMagazinsItemsMap(self):
        query= ('select idMagazins, itemName, ItemQty, Items.idItem from Magazins,'+
        ' Items where Magazins.ItemId=Items.idItem')
        result=self._getDataFromDB(query)
        return result
    
    def _getDataFromDB(self, query):
        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
            
        except:
            self.errWindow=Errors(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
            return None
        finally:
            cur.close()
            conn.close()
        
        return result        
               
    def saveMagazinsMapping(self, magazinesMap):
        pass  
    
    def _updateMagazine(self, param):
        pass
    
    def _insertMagazine(self, param):
        pass
    
    def dropMagazinesTable(self):
        pass 
        