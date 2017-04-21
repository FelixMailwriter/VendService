# -*- coding:utf-8 -*-

import mysql.connector
from mysql.connector import Error
from ConfigParser import ConfigParser
import Errors


class DbConnector():

    def __init__(self):
            self.errWindow=Errors.Errors("")
             
    def getConnection(self):
        conn=None
        dbconfig=self.getDBConfig(filename='config.ini', section='mysql') 
        try:
            conn=mysql.connector.connect(**dbconfig)
                
        except Error as e:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')
            print (e)
            
        return conn
        
                
    def getDBConfig(self, **param):
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
    
    def getDataFromDb(self, query):
        try:
            conn=self.getConnection()
            cur=conn.cursor()
            cur.execute(query)
            result = cur.fetchall()            
            
        except:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')

        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return result
    
    def insertDataToDB(self, query):
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
        try:
            conn=self.getConnection()
            cur=conn.cursor()
            cur.execute(query)
            conn.commit()
        except:
            self._showError(u'Ошибка', u'Ошибка подключения к базе данных')
            return False
        finally:
            cur.close()
            conn.close()
        return True  
    
    def _showError(self, header, message): 
        self.message=Errors(message)
        self.message.window.setWindowTitle(header)
        self.message.window.show()         

          