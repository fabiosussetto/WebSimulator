'''
Created on May 2, 2011

@author: fabio
'''

import sys
import time
import simulation
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *


class Form(QDialog):
    
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.simulator = simulation.Simulator()
        
        self.urlBar = QLineEdit()
        self.urlGo = QPushButton("Vai")
        self.btnSimulate = QPushButton("Run test")
        self.connect(self.btnSimulate, SIGNAL("clicked()"), self._onSimulateClicked)
        
        self.simulator.createView()
        self.browser = self.simulator.getWidget()
        self.browser.show()
        
        urlLayout = QHBoxLayout()
        urlLayout.addWidget(self.urlBar)
        urlLayout.addWidget(self.urlGo)
        
        layout = QVBoxLayout()
        layout.addLayout(urlLayout)
        layout.addWidget(self.browser)
        layout.addWidget(self.btnSimulate)
        self.setLayout(layout)
        
        self.setWindowTitle("Test Webkit")
        self.resize(1100, 650)
        self.simulator.load('http://www.trenitalia.it')
        #self.simulator.load('http://www.alistapart.com')
        
    def _onSimulateClicked(self):
        self.simulator.click('#menu1 > li:first > a', True)
        #self.simulator.click('#menu1 > li:nth-child(2) > a', True)
        self.simulator.fill('#stazin', 'torino')
        self.simulator.fill('#stazout', 'milano')
        self.simulator.click('.btnInviaCrusc', True)
        #self.simulator.fill('#search', 'test')
        #self.simulator.fill('#search', 'test2')
        #self.simulator.runjs('alert("cia");')
        #self.simulator.runjs('alert("cia2");')
        #self.simulator.click('#submit', True)
        
        
if __name__ == '__main__':
    pass


app = QApplication(sys.argv)
form = Form() 
form.show() 
app.exec_()