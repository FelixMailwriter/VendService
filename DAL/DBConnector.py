# -*- coding:utf-8 -*-

import mysql.connector
from PyQt4.Qt import QMessageBox
from mysql.connector import Error
from ConfigParser import ConfigParser
import base64
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
            #raise Exception('{0} not found in {1} file'.format(section, filename))
            self.errWindow.setMessageText(u"Ошибка файла конфигурации БД. Отсутствует секция.")
            self.errWindow.window.show()            
        return config
    
    def getItems(self):
        try:
            conn=self.getConnection()
            cur=conn.cursor()
        except:
            print ('DataBase is NOT connected')
            self.errWindow.setMessageText(u"Ошибка подключения к базе данных")
            self.errWindow.window.show()
            return
            
        cur.execute('SELECT idItem, itemName, ItemPrice from Items')
        result = cur.fetchall()
        conn.close()
        return result
        
    def addItem(self, icon, **params):
        
        itemName=params["ItemName"]
        itemPrice=params["ItemPrice"]
        itemIcon=icon #params["ItemIcon"]
        
        try:
            conn=self.getConnection()
            cur=conn.cursor()
            picbyte=base64.b64encode(itemIcon)
            query='''Insert into vending.Items (ItemName, ItemPrice, ItemIcon) values ('%s', %d, '%s')''' %(itemName, itemPrice, picbyte)
            cur.execute(query)
            
            if cur.lastrowid:
                message=QMessageBox()
                message.setText(u"Данные добавлены")
                message.exec_()
            else:
                message=QMessageBox()
                message.setText(u"Ошибка добавления данных")
                message.exec_()
        
            conn.commit()
            
        except Error as error:
            print (error)
            
    def editItem (self, icon, **params):
        itemId=params["ItemId"]
        itemName=params["ItemName"]
        itemPrice=params["ItemPrice"]
        itemIcon=icon
    
    def getItemIconById(self, id):
        pass    
        
          