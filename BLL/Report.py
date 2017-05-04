# -*- coding:utf-8 -*-

from PyQt4.Qt import QObject, QStringList
from DAL.DBConnector import DbConnector
import datetime
from Errors import Errors
from Printer.PrnDK350 import Printer

class ReportController(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.printer=Printer()
        
        #Прописываем события кнопок
         ############

    def printXReport(self):
        self.printer.printXReport()
        
    def printZReport(self):
        self.printer.printZReport()
        
    def getStatus(self):
        try:
            self.printer.getStatus()
        except AttributeError:
            self.message=Errors(u"Принтер не найден")
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show() 

            
        
        
          