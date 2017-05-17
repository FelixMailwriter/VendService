# -*- coding:utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.Qt import QObject, QHeaderView
from DAL.DBConnector import DbConnector
import datetime
import time
import Printer.PrnDK350 as Printer
from Errors import Errors

class ReportController(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.DbConnector=DbConnector()
        self.form=form.window
        self.printer=Printer.Printer()
        
        #Прописываем события кнопок
        self.form.btn_XReport.clicked.connect(self._printXReport)
        self.form.btn_ZReport.clicked.connect(self._printZReport)
        self.form.btn_ZReportByNum.clicked.connect(self._printZReportByNum)
        self.form.btn_Inkass.clicked.connect(self._inkass)
        self.form.btn_PrnStatus.clicked.connect(self._getPrnStatus)
        self.form.btn_GetLog.clicked.connect(self._getLog)
        self.form.btn_ClearLog.clicked.connect(self._clearLog)
        
        self._getPrnStatus()

    def _printXReport(self):
        try:
            logMessages=self.printer.checkStatus()
            self.DbConnector.writeLog(logMessages)
            self.printer.printXReport('3')
        except Printer.PrinterHardwareException as e:
            self.emit(QtCore.SIGNAL('Printer is not ready'), e.value)
            
    def _printZReport(self):
        logMessages=self.printer.checkStatus()
        self.DbConnector.writeLog(logMessages)
        self.printer.printZReport()
    
    def _printZReportByNum(self):
        begin=self.form.spn_Begin.value()
        end=self.form.spn_End.value()
        if begin==0 or end==0:
            return
        if begin<=end:
            self.printer.printZReportByNum(begin, end)
        else:
            self._showMessage(u'Результат операции', u"Неправильный ввод")
    
    def _inkass(self):
        InkassInfo=self.DbConnector.getInfoForInkass()
        
        #if InkassInfo[0] is None:
        #    self._showMessage(u'Результат операции', u"Продажи отсутствуют.")
        #    return
        accountedCash=InkassInfo[0]
        idLastInkass=InkassInfo[1]
        dateLastInkass=InkassInfo[2]
        cash=self.DbConnector.getCashInNoteReseiver(dateLastInkass)[0]
        if cash is None:
            cash=0
        context=[]
        context.append(dict(Text=''))
        header='Encashment order %d:' %((idLastInkass+1))
        context.append(dict(Text='{:^35}'.format(header)))
        context.append(dict(Text=''))
        context.append(dict(Text='{:^35}'.format('Begin of period: '+str(dateLastInkass))))
        context.append(dict(Text='{:^35}'.format('End of period: '+str(datetime.datetime.now()))))
        context.append(dict(Text='--------------------------------------'))
        context.append(dict(Text=''))
        context.append(dict(Text='{:<35}{:>4}'.format('Summ of sales: ', str(accountedCash))))
        context.append(dict(Text=''))
        context.append(dict(Text='{:<35}{:>4}'.format('Unaccounted sum: ', str(cash-accountedCash))))
        context.append(dict(Text=''))
        context.append(dict(Text='{:<35}{:>4}'.format('Total sum: ', str(cash))))
        context.append(dict(Text=''))        
        context.append(dict(Text='--------------------------------------'))
        
        for s in context:
            st=s['Text']
            print st
            
        if self.DbConnector.writeInkass(accountedCash):
            self._showMessage(u'Результат операции', u'Инкассация проведена')
        else:
            self._showMessage(u'Результат операции', u'Ошибка инкассации')
            
        self.printer.run(context, checkType='NotFisk')
        time.sleep(3)
        self.printer.printZReport()
            
    def _getPrnStatus(self):
        try:
            logList=self.printer.checkStatus()
            statusReport=''
            for log in logList:
                statusReport+=log .message+'\n'
            self.form.pte_prnStatus.setPlainText(statusReport)
            self.form.pte_prnStatus.setReadOnly(True)    
        except Printer.PrinterHardwareException as e:
            self.message=Errors(e.value)
            self.message.window.setWindowTitle(u'Ошибка')
            self.message.window.show()            

    def _getLog(self):
        self.form.tbw_Log.setRowCount(0)
        result=self.DbConnector.getLog()
        if len(result)==0:
            return
        self.form.tbw_Log.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.form.tbw_Log.horizontalHeader().setResizeMode(1,QHeaderView.ResizeToContents)
        self.form.tbw_Log.horizontalHeader().setResizeMode(2,QHeaderView.ResizeToContents)
        self.form.tbw_Log.horizontalHeader().setResizeMode(3,QHeaderView.Stretch)
        counter=0
        for row in result:
            ItemEventType=QtGui.QTableWidgetItem(str(row[0]))
            ItemSource=QtGui.QTableWidgetItem(str(row[1]))
            ItemEventDate=QtGui.QTableWidgetItem(str(row[2]))
            ItemEvent=QtGui.QTableWidgetItem(row[3])
            
            self.form.tbw_Log.insertRow(counter)
            self.form.tbw_Log.setItem(counter,0,ItemEventType)
            self.form.tbw_Log.setItem(counter,1,ItemSource)
            self.form.tbw_Log.setItem(counter,2,ItemEventDate)
            self.form.tbw_Log.setItem(counter,3,ItemEvent)
            
    def _clearLog(self):
        self.form.tbw_Log.setRowCount(0)
        self.DbConnector.clearLog('Printer')
        
    def _showMessage(self, header, message):
        self.message=Errors(message)
        self.message.window.setWindowTitle(header)
        self.message.setParent(self)
        self.message.window.show()         
            
          