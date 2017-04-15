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
            print ('DataBase is NOT connected')
            self.errWindow.setMessageText(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
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
            self.errWindow.setMessageText(u"Ошибка файла конфигурации БД. Отсутствует секция.")
            self.errWindow.window.show()            
        return config
    
    
    def getItemIconById(self, id):
        pass    
        
          