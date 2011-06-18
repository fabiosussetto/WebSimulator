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
        
        self.connect(self.simulator, SIGNAL("loadingPage()"), self._onLoadingPage)
        self.connect(self.simulator, SIGNAL("pageLoaded()"), self._onPageLoaded)
        
        self.browser.show()
        
        self.loadingLabel = QLabel('Loading page ...')
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        self.loadingLabel.hide()
        
        urlLayout = QHBoxLayout()
        urlLayout.addWidget(self.urlBar)
        urlLayout.addWidget(self.urlGo)
        
        layout = QVBoxLayout()
        layout.addLayout(urlLayout)
        layout.addWidget(self.browser)
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.btnSimulate)
        self.setLayout(layout)
        
        self.setWindowTitle("Test Webkit")
        self.resize(1100, 650)
        self.simulator.load('http://www.trenitalia.it')
        
    def _onSimulateClicked(self):
        self.simulator.click('#menu1 > li:first > a', True)
        self.simulator.assertPageTitle(r"orari e acquisto")
        self.simulator.fill('#stazin', 'torino')
        self.simulator.fill('#stazout', 'milano')
        self.simulator.click('.btnInviaCrusc', True)
        
        self.simulator.assertTextMatch('torino', '.detagglio td:first')
        self.simulator.assertTextMatch('milano', '.detagglio td:eq(1)')
        
        self.simulator.click('form[name=dati] table:eq(1) input[type=radio]:first')
        self.simulator.clickLinkMatching('procedi', 'a')
        
    
    def _onLoadingPage(self):
        self.loadingLabel.show()  
        
    def _onPageLoaded(self):
        self.loadingLabel.hide()  
        
if __name__ == '__main__':
    pass


app = QApplication(sys.argv)
form = Form() 
form.show() 
app.exec_()