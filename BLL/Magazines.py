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
        self.fillItemList()
        
    def getItemsList(self):
        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
            cur.execute('select ItemName from Items order by ItemName')
            result = cur.fetchall()
            
        except:
            print ('DataBase is NOT connected')
            self.errWindow=Errors(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
  
        finally:
            cur.close()
            conn.close()
            
        listItems=QStringList()
        for element in result:
            listItems.append(element[0]) 
                        
        self.form.setItemsList(listItems)     
           

    def fillItemList(self):
        try:
            conn=self.DbConnector.getConnection()
            cur=conn.cursor()
            cur.execute('select idMagazins, itemName, ItemQty, Items.idItem from Magazins,'+ 
            'Items where Magazins.ItemId=Items.idItem')
            result = cur.fetchall()
            
        except:
            print ('DataBase is NOT connected')
            self.errWindow=Errors(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
  
        finally:
            cur.close()
            conn.close()
               
        self.form.fillMagazinsTable(result)
        
    def saveMagazinsMapping(self, magazinesMap):
        pass   
        