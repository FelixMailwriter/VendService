# -*- coding:utf-8 -*-
from PyQt4 import QtCore
import serial
from ConfigParser import ConfigParser
from enum import __repr__


class Printer(QtCore.QThread):
    def __init__(self, items, checkType='NotFisk'):
        QtCore.QThread.__init__(self)
        self.prn_config=self._getSettings()
        self.devPath=self.prn_config['path']    #Путь к принтеру
        self.items=items                        #Содержимое чека (предметы или строки текста)
        self.prn=None                           #ссылка на порт принтера
        self.command=None                       #команда принтеру
        self.SEQ=0x20                           #Порядковый номер команды
        self.checkType=checkType

    def run(self):
        self.prn=self._getConnection(self.devPath)
        self._printCheck()
        
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
        conn = serial.Serial()
        conn.port = devPath
        if conn is None:
            raise PrinterHardwareException('Device not found') 
                
        conn.baudrate = 115200
        conn.bytesize = serial.EIGHTBITS    #number of bits per bytes
        conn.parity = serial.PARITY_NONE    #set parity check: no parity
        conn.stopbits = serial.STOPBITS_ONE #number of stop bits
        conn.timeout = None                 #block read
        conn.xonxoff = False                #disable software flow control
        conn.rtscts = True                  #disable hardware (RTS/CTS) flow control
        conn.dsrdtr = True                  #disable hardware (DSR/DTR) flow control
        return conn
    
    def _printCheck(self):
        #Открываем порт
        self.prn.open()
        if self.checkType=='Fisk':
            self._printFiskCheck()
        elif self.checkType=='NotFisk':
            self._printNotFiskCheck()
    
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
                bytesParam.append(asciiCode)        #Если просто симовл  записываем его ascii-код
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
            l=self.prn.in_waiting
            if l>0:
                data=self.prn.read(l)
                print 'answer received'
                print 'data length ' 
                print len(data)
                self.showRecevedData(data)
                print data
                return data
            self.msleep(100)

    def showRecevedData(self, data):
        #распечатка данных от принтера
        print '---------------'
        print 'Reseived data:'
        for i in range(0, len(data)):
            print data[i].encode('hex') 
        print '---------------'        
            
    def _checkAnswer(self, answer):
        pass
        

class PrinterHardwareException(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return __repr__(self.value) 
    