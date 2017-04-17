# -*- coding:utf-8 -*-

from PyQt4.Qt import QObject, QFont, QHeaderView

class MagazinesController(QObject):

    def __init__(self, form):
        QObject.__init__(self)
        self.form=form
        self.setUpTable()
        self.fillItemList()
        
        
    def setUpTable(self):
       table=self.form.window.tblw_Magazines
       table.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
       table.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
       table.horizontalHeader().setResizeMode(2,QHeaderView.Stretch)
       table.horizontalHeader().setResizeMode(3,QHeaderView.Stretch) 

    def fillItemList(self):
          pass