# -*- coding:utf-8 -*-

import mysql.connector
from mysql.connector import Error
from ConfigParser import ConfigParser
from Errors import Errors
from datetime import datetime


class DbConnector():

    def __init__(self):
        pass
             
    def getConnection(self):
        conn=None
        dbconfig=self._getDBConfig(filename='config.ini', section='mysql') 
        try:
            conn=mysql.connector.connect(**dbconfig)
                
        except Error as e:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')
            print (e)
            
        return conn
        
                
    def _getDBConfig(self, **param):
        filename=param['filename']
        section=param['section']
        parser=ConfigParser()
        parser.read(filename)
        config={}
        if parser.has_section(section):
            items=parser.items(section)
            for item in items:
                config[item[0]]=item[1]
        else:
            self._showError(u'Ошибка', u'Ошибка файла конфигурации БД. Отсутствует секция.')
        return config
    
    def getDataFromDb(self, query, type='all'):
        conn = cur = None
        try:
            conn=self.getConnection()
            cur=conn.cursor()
            cur.execute(query)
            if type=='all':
                result = cur.fetchall()
            if type=='one':
                result=cur.fetchone()            
            return result
        except:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')
            
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()     
    
    def insertDataToDB(self, query):
        conn = cur = None
        try:
            conn=self.getConnection()
            cur=conn.cursor()
            cur.execute(query)
            conn.commit()
            return True
            
        except:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')
            return False
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close() 
        
    def deleteDataFromTable(self, query):
        conn = cur = None
        try:
            conn=self.getConnection()
            cur=conn.cursor()
            cur.execute(query)
            conn.commit()
        except:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')
            return False
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return True
    
    def writeLog(self, logMessages):
        for logMessage in logMessages:
            priority=logMessage.priority
            source=logMessage.sourse
            event=logMessage.message
            query='Insert into Log (EventType, Source, EventDate, Event)'+\
                ' values (\'%s\', \'%s\', \'%s\', \'%s\')' \
                %(priority, source, str(datetime.now()), event)
            self.insertDataToDB(query)  
    
    def getLog(self):
        query='Select EventType, Source, EventDate, Event from Log Where Source like \'Printer\''
        result=self.getDataFromDb(query, 'all')
        return result
    
    def _showError(self, header, message): 
        self.message=Errors(message)
        self.message.window.setWindowTitle(header)
        self.message.window.show()         

          