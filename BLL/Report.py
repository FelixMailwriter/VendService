# -*- coding:utf-8 -*-

from PyQt4.Qt import QObject, QStringList
from DAL.DBConnector import DbConnector
import datetime
from Errors import Errors
import Printer.PrnDK350 as Printer

class ReportController(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.printer=Printer.Printer()
        
        #Прописываем события кнопок
         ############

    def printXReport(self):
        self.printer.printXReport()
        
    def printZReport(self):
        self.printer.printZReport()
        
    def checkStatus(self):
        try:
            self.printer.checkStatus()
        except Printer.PrinterHardwareException as e:
            self.message=Errors(e.value)
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show() 

            
        
        
          