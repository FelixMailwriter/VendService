# -*- coding:utf-8 -*-

import os
from PyQt4 import QtCore, uic
from PyQt4.Qt import QObject
from BLL.ItemsController import ItemsController
from Magazines import MagazinesController
from Report import ReportController
from Errors import Errors
from BDManagement import BDManagement


class HApp(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.form=MainWindow()
        self.form.window.show()
        
class MainWindow(QObject):
        
    def __init__(self):
        QObject.__init__(self)
        path=os.path.abspath("UI/UIForms/mainForm.ui")
        
        self.window=uic.loadUi(path)

        # Создаем контроллеры
        self.ItemsController=ItemsController(self)
        self.MagazinesController=MagazinesController(self)
        self.ReportController=ReportController(self)
        
        self.DBController=BDManagement(self) #удалить на рабочей машине

        #Подписываемся на событие "Принтер не найден"
        self.connect(self.MagazinesController, QtCore.SIGNAL("Printer is not ready"), self._prnIsNotFound)
        self.ItemsController.ItemDeleted.connect(self.MagazinesController.setUpMagazinsTable)
        
        self.setUpTables()
        
    def setUpTables(self):
        self.ItemsController.setUpItemsTable()        
        self.MagazinesController.setUpMagazinsTable()

    def _prnIsNotFound(self, message):
        self.message=Errors(message)
        self.message.window.setWindowTitle(u'Ошибка')
        self.message.window.show()

