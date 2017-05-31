# -*- coding:utf-8 -*-
from PyQt4 import QtCore
import serial
from ConfigParser import ConfigParser
from enum import __repr__
import binascii
from Common.Logs import LogEvent


class Printer(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.prn_config=self._getSettings()
        self.devPath=self.prn_config['path']    #Путь к принтеру
        self.prn=None                           #ссылка на порт принтера
        self.command=None                       #команда принтеру
        self.SEQ=0x20                           #Порядковый номер команды
        self.status=[]
        self.prn=self._getConnection(self.devPath)

    def run(self, items, checkType='NotFisk'):
        self.items=items
        self.checkType=checkType
        self._printCheck()


    def printXReport(self, type='0'): 
         #Информация о накоплениях за день
        #Открываем порт
        self._openPort()         
        self._sendCommand(0x45, type)
        self.msleep(100)
        self._getAnswer()
        self._closePort()
        #self.prn.close()
        
    def printZReport(self):
        #Открываем порт
        self._openPort()         
        self._sendCommand(0x78, 'K,3')
        self.msleep(100)
        self._getAnswer()
        self._closePort()
        #self.prn.close()
        
        
    def printZReportByNum(self, start, end):
        self._openPort()         
        self._sendCommand(0x49, '%d,%d' %(start, end))
        self._closePort()        

    def checkStatus(self):
        ready=True
        errormsg=''
        logList=[]       
        statusBytes=self._getStatusBytes()

        if statusBytes[0][2]=='1':
            log=LogEvent('Warning', 'Printer', u'Часы принтера не установлены')
            logList.append(log)
        if statusBytes[1][5]=='1':
            log=LogEvent('Info', 'Printer', u'Замок бумаги открыт')
            logList.append(log) 
            ready=False 
            errormsg+=u'Замок бумаги открыт. '          
        if statusBytes[2][1]=='1':
            log=LogEvent('Warning', 'Printer', u'Мало бумаги')
            logList.append(log)            
        elif statusBytes[2][0]=='1':
            log=LogEvent('Critical', 'Printer', u'Бумага окончилась')
            logList.append(log)
            ready=False
            errormsg+=u'Бумага закончилась. '              
        if statusBytes[4][4]=='1':
            log=LogEvent('Critical', 'Printer', u'Фискальная память заполнена')
            logList.append(log)
        elif statusBytes[4][3]=='1':
            log=LogEvent('Warning', 'Printer', u'В фискальной памяти осталось менее 50 записей')
            logList.append(log)
        elif statusBytes[2][6]=='1':
            log=LogEvent('Warning', 'Printer', u'В фискальной памяти осталось менее 2000 байт')
            logList.append(log)
        elif statusBytes[2][4]=='1':
            log=LogEvent('Warning', 'Printer', u'В фискальной памяти осталось менее 3000 байт')
            logList.append(log)
        elif statusBytes[2][2]=='1':
            log=LogEvent('Warning', 'Printer', u'В фискальной памяти осталось менее 4000 байт')
            logList.append(log)
        if statusBytes[5][0]=='1':
            log=LogEvent('Critical', 'Printer', u'Фискальная память в режиме ТОЛЬКО_ЧТЕНИЕ')
            logList.append(log)
        
        if not ready:
            raise PrinterHardwareException(u"Принтер не готов. "+errormsg)
        return logList            
                    
    def _getStatusBytes(self):
        status=[]
        self._openPort()               
        self._sendCommand(0x4A, '')
        self.msleep(100)
        answer=self._getAnswer()
        beginRead=False
        if answer is None:
            self.prn.close()
            raise PrinterHardwareException(u'Принтер не найден')
            return
        for statusByte in answer:
            statusByte=statusByte.encode('hex')
            if statusByte=='04':
                beginRead=True
                continue
            if statusByte=='05':
                self.prn.close()
                return status 
            if beginRead:
                byteStr=self._byte2bits(statusByte)
                byteStr=byteStr[2:]
                revertStr=byteStr[::-1]
                status.append(revertStr)
                print status
        self._closePort()
        return status                
               
    def _getSettings(self):
        filename='config.ini'
        section='printer'
        parser=ConfigParser()
        parser.read(filename)
        prn_config={}
        if parser.has_section(section):
            items=parser.items(section)
            for item in items:
                prn_config[item[0]]=item[1]
        else:
            self._showError(u'Ошибка', u'Ошибка файла конфигурации. Отсутствует секция принтера.')
        return prn_config

    def _getConnection(self, devPath):
        try:
            conn = serial.Serial()
            conn.port = devPath
        except :
            raise PrinterHardwareException(u'Принтер не найден') 
                
        conn.baudrate = 115200
        conn.bytesize = serial.EIGHTBITS    #number of bits per bytes
        conn.parity = serial.PARITY_NONE    #set parity check: no parity
        conn.stopbits = serial.STOPBITS_ONE #number of stop bits
        conn.timeout = None                 #block read
        conn.xonxoff = False                #disable software flow control
        conn.rtscts = True                  #disable hardware (RTS/CTS) flow control
        conn.dsrdtr = True                  #disable hardware (DSR/DTR) flow control
        return conn
    
    def _openPort(self):
        try:
            self.prn.open()
        except :
            raise PrinterHardwareException(u'Принтер не найден')
        
    def _closePort(self):
        if self.prn.isOpen():
            self.prn.close()
        
    def _printCheck(self):
        #Открываем порт
        self._openPort() 
        if self.checkType=='Fisk':
            self._printFiskCheck()
        elif self.checkType=='NotFisk':
            self._printNotFiskCheck()
        self._closePort()
    
    def _printFiskCheck(self):
            #Открываем фискальный чек
            self._sendCommand(0x30,'1,00000,1')            
            #Печать продаваемых товаров   
            for item in self.items:
                if item['Price']==None:
                    #Если печатать свободный текст предмета
                    self._sendCommand(0x36,item['Text'])
                else:
                    #Если печатаем описание предмета (имя и цена)
                    fiskItemParameters=self._getfiskItemParameters(item['Text'], item['TaxCode'], item['Price'])
                    self._sendCommand(0x34,fiskItemParameters)
            #Записываем итоговую сумму
            self._sendCommand(0x35, '')
            #Закрываем фискальный чек
            self._sendCommand(0x38, '')
    
    def _printNotFiskCheck(self):
        #Открываем не фискальный чек
        self._sendCommand(0x26,'') 
        #Печать содержимого нефискального чека   
        for item in self.items:
            self._sendCommand(0x2A,item['Text'])
        #Закрываем не фискальный чек
        self._sendCommand(0x27, '')                
            
    def _getfiskItemParameters(self, text, taxCode, price):
        #Формирование строки параметров для фискального чека (Название, кодНДС, Цена)
        params=r'{}{}{}{}'.format(text, '\t',taxCode, price)  
        return params
    
    def _sendCommand(self, commandCode, commandParams):
        command=self._makeCommand(commandCode, commandParams)
        self.prn.write(command)
        #self._getAnswer()

    def _makeCommand(self, commandCode, commandParams):
        self.SEQ+=1                                     #Увеличиваем счетчик команд на 1
        params=self._getParamsBytes(commandParams)      #Получем байтовый массив строки параметров
        paramsLength=len(params)                        #Подсчитываем длину массива строки параметров
        packadgeLength=10+paramsLength                  #Подсчитываем длину пакета (команда + параметры)
        command=bytearray(packadgeLength)          
        commandLength=4+paramsLength                    #Подсчитываем длину команды
        #Записываем в пакет байты длины строки, номера команды и кода команды
        command[0]=0x01
        command[1]=commandLength+0x20
        command[2]=self.SEQ
        command[3]=commandCode
        #Записываем байты строки параметров команды
        pos=4
        for b in params:
            command[pos]=b
            pos+=1
        #записываем байт признака конца команды
        command[pos]=0x05
        #получаем контрольную сумму
        bcc=self._getBCC(command, paramsLength)
        #дописываем байты контрольной суммы
        pos+=1
        for i in range(0,4):
            command[pos]=bcc[i]
            pos+=1
        #дописываем байт признака конца пакета
        command[packadgeLength-1]=0x03
        return command

    def _getParamsBytes(self, commandParams):
        seqParamSymbols=[]                          #Параметры, разбитые по символам
        for commparam in commandParams:
            param=commparam
            for symbol in param:
                seqParamSymbols.append(symbol)      #Получаем список параметров команды посимвольно
        lenParamsString=len(seqParamSymbols)
        bytesParam=bytearray()
        #Записываем в массив ascii коды символов команды
        for i in range(0, lenParamsString):
            p=seqParamSymbols[i]
            asciiCode=ord(seqParamSymbols[i])
            if asciiCode==9:                        #если встретился символ '\t'
                bytesParam.append(0x9)              # записываем управляющий символ табуляции
            elif asciiCode>=48 and asciiCode<=57:   #Если встретилась цифра
                num=int(chr(asciiCode),16)          #записываем ее ascii-коды прибаляя к нему 0x30
                bytesParam.append(num+0x30)
            else:
                bytesParam.append(asciiCode)        #Если просто симовол  записываем его ascii-код
        return bytesParam

    def _getBCC(self, command, paramsLength):
        bccsum=0
        #получаем сумму байт строки команды + параметров 
        for i in range(1, (paramsLength+5)):
            bccsum+=command[i]
        hexSum=hex(bccsum)
        #разделяем значения по одной цифре и прибавляем к ней 0x30
        bcc=bytearray(4)
        for i in range (0,4): bcc[i]=0x30
        count=3
        for i in range(len(hexSum)-1, 0, -1):
            if hexSum[i]=='x': break
            bcc[count]=int(hexSum[i],16)+0x30
            count-=1
        return bcc
                
    def _getAnswer(self):
        #получение данных от принтера
        print 'wait for answer...'
        for i in range (1,4):
            print 'iter %d' %(i)
            l=self.prn.in_waiting
            print l
            if l>0:
                data=self.prn.read(l)
                print 'answer received'
                print 'data length ' 
                print len(data)
                self.showRecevedData(data)
                return data
            self.msleep(1000)
          
    def showRecevedData(self, data):
        #распечатка данных от принтера
        print '---------------'
        print 'Reseived data:'
        s=''
        for i in range(0, len(data)):
            s+=data[i].encode('hex') + ' '
        print s 
        print '---------------'        
            
    def _byte2bits(self,hex_string):
        n = len(hex_string)
        p= binascii.unhexlify(hex_string.zfill(n + (n & 1)))   
        a=bin(int(binascii.hexlify(p), 16))
        return a
        
class PrinterHardwareException(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return __repr__(self.value) 
    