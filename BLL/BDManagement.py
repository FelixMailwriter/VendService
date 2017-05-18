# -*- coding:utf-8 -*-

from PyQt4 import QtCore
from PyQt4.Qt import QObject
from DAL.DBConnector import DbConnector

class BDManagement(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form.window
        
        #Прописываем события кнопок
        self.form.btn_delItemsTable.clicked.connect(self._delItemsTable)
        self.form.btn_delMovementsTable.clicked.connect(self._delMovementsTable)
        self.form.btn_delSalesTable.clicked.connect(self._delSalesTable)
        self.form.btn_delInkasTable.clicked.connect(self._delInkasTable)
        self.form.btn_delLogs.clicked.connect(self._delLogs) 
        self.form.btn_clearAll.clicked.connect(self._clearAll)  
     
    def _delItemsTable(self):
        query='delete from Items '+\
                'where idItem not in (select distinct itemId from Magazins) '+\
                'and idItem not in (select distinct idItem from ItemsMovements)'
        self.DbConnector.deleteDataFromTable(query)
    
    def _delMovementsTable(self):
        query='delete from ItemsMovements'
        self.DbConnector.deleteDataFromTable(query)
        
    def _delSalesTable(self):
        query='delete from Sales'
        self.DbConnector.deleteDataFromTable(query)
    
    def _delInkasTable(self):
        query='delete from Incas'
        self.DbConnector.deleteDataFromTable(query)
        query='delete from ReceivedNotes'
        self.DbConnector.deleteDataFromTable(query)
    
    def _delLogs(self):
        query='delete from Log'
        self.DbConnector.deleteDataFromTable(query)  
    
    def _clearAll(self):
        self._delMovementsTable()
        self._delItemsTable()
        self._delSalesTable()
        self._delInkasTable()
        self._delLogs()
        
        
        
    