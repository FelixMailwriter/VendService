# -*- coding:utf-8 -*-

from PyQt4.Qt import QObject, QStringList
from DAL.DBConnector import DbConnector
import datetime
from Errors import Errors
import Printer.PrnDK350 as Printer
from Errors import Errors

class ReportController(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form
        self.printer=Printer.Printer()
        
        #Прописываем события кнопок
        self.form.window.btn_PrnStatus.clicked.connect(self._getPrnStatus)

    def printXReport(self):
        self.printer.printXReport()
        
    def printZReport(self):
        self.printer.printZReport()
        
    def _getPrnStatus(self):
        try:
            logList=self.printer.checkStatus()
            statusReport=''
            for log in logList:
                statusReport+=log .message+'\t'
            a=0            
        except Printer.PrinterHardwareException as e:
            self.message=Errors(e.value)
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()            


            
        
        
          