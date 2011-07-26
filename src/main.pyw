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
from test_cases import wp3testcase, wp2testcase


class Form(QDialog):
    
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.simulator = simulation.Simulator()
        
        self.urlBar = QLineEdit()
        self.urlGo = QPushButton("Vai")
        self.btnSimulate = QPushButton("Run test")
        self.btnPicker = QPushButton("Picker")
        self.connect(self.btnSimulate, SIGNAL("clicked()"), self._onSimulateClicked)
        
        self.simulator.createView()
        self.browser = self.simulator.getWidget()
        
        self.connect(self.simulator, SIGNAL("loadingPage()"), self._onLoadingPage)
        self.connect(self.simulator, SIGNAL("pageLoaded()"), self._onPageLoaded)
        
        self.browser.show()
        
        self.loadingLabel = QLabel('Loading page ...')
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        self.loadingLabel.hide()
        
        self.pathLabel = QLabel()
        #self.pathLabel.hide()
        
        urlLayout = QHBoxLayout()
        urlLayout.addWidget(self.urlBar)
        urlLayout.addWidget(self.urlGo)
        urlLayout.addWidget(self.btnPicker)
        
        layout = QVBoxLayout()
        layout.addLayout(urlLayout)
        layout.addWidget(self.browser)
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.pathLabel)
        layout.addWidget(self.btnSimulate)
        self.setLayout(layout)
        
        self.setWindowTitle("Test Webkit")
        self.resize(1100, 650)
        
        self.simulator.load_js()
        self.simulator.load('http://wptesi/wp_3-1-3/')
        
        
    def _onSimulateClicked(self):
        test_case = wp3testcase.Wp3TestCase(self.simulator)
        test_case.run()
        
        #test_case = wp2testcase.Wp2TestCase(self.simulator)
        #test_case.run()
        
    
    def _onLoadingPage(self):
        self.loadingLabel.show()  
        
    def _onPageLoaded(self):
        self.loadingLabel.hide()
        
    def _onPathPicked(self, path):
        self.pathLabel.setText(path)
        
if __name__ == '__main__':
    pass


app = QApplication(sys.argv)
form = Form() 
form.show() 
app.exec_()