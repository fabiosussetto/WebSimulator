'''
Created on May 2, 2011

@author: Fabio Sussetto
'''

import sys
import time
import simulation
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from test_cases import wp3testcase, wp2testcase
import qrc_resources
from ui.assertion_dialog import AssertionDlg
from simulation.actions import *
from utilities import *

MyBorderRole = Qt.UserRole + 1

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.actionsModel = simulation.actions.TreeModel()
        self.simulator = simulation.Simulator(self.actionsModel)
        
        self.mainSplitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.mainSplitter)
        splitterLeft = QWidget()
        splitterRight = QWidget()
        splitterRight.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.mainSplitter.addWidget(splitterLeft)
        
        self._buildAddressBar()
        
        self._buildWebView()
        
        self._buildActionsTree()
        
        self.mainSplitter.addWidget(splitterRight)
        
        rightLayout = QVBoxLayout(splitterRight)
        
        rightLayout.addWidget(self.treeWidget)
        actionsToolbox = QHBoxLayout()
        actionsToolbox.setAlignment(Qt.AlignLeft)
        rightLayout.addLayout(actionsToolbox)
        
        actionsToolbox.addWidget(self.btnPlayAction)
        actionsToolbox.addWidget(self.btnRemoveAction)
        actionsToolbox.addWidget(self.btnClearAction)
        
        layout = QVBoxLayout(splitterLeft)
        layout.addLayout(self.urlLayout)
        self.browser.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout.addWidget(self.browser)
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.pathLabel)
        
        self.setWindowTitle("Web Acceptance Testing")
        self.setMinimumSize(1200, 600)
        
        self.buildActions()
        
        self.simulator.load_js()
        self.simulator.load('http://wptesi/wp_3-1-3/wp-admin')
        #self.simulator.load('http://wptesi/wp_3-1-3/wp-admin')
        
        self.actionsModel.loadFromXml(os.path.join(os.path.dirname(__file__), "sample_tests/good_1.xml"))
        
    def openAssertionDlg(self, pickedData):
        self.assertionDlg = AssertionDlg(self.actionsModel, pickedData, self)
        self.assertionDlg.setModal(False)
        self.assertionDlg.show()
        
    def _buildAddressBar(self):
        self.urlBar = QLineEdit()
        self.urlGo = QPushButton("Visit")
        self.connect(self.urlGo, SIGNAL("clicked()"), self._onUrlGo)
        self.connect(self.simulator.webframe, SIGNAL("urlChanged(QUrl)"), self._onUrlChanged)
        self.urlLayout = QHBoxLayout()
        self.urlLayout.addWidget(self.urlBar)
        self.urlLayout.addWidget(self.urlGo)

    def _buildWebView(self):
        self.simulator.createView()
        self.browser = self.simulator.getWidget()
        #self.browser.setMinimumWidth(900)
        self.connect(self.simulator, SIGNAL("loadingPage()"), self._onLoadingPage)
        self.connect(self.simulator, SIGNAL("pageLoaded()"), self._onPageLoaded)
        self.connect(self.simulator.picker, SIGNAL("pathPicked(PyQt_PyObject)"), self._onPathPicked)
        self.browser.show()
        self.loadingLabel = QLabel('Loading page ...')
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        self.loadingLabel.hide()
        #self.pathLabel = QLabel()
        self.pathLabel = QLineEdit()
        self.pathLabel.setReadOnly(True)

    def _buildActionsTree(self):
        self.treeWidget = QTreeView()
        self.treeWidget.setModel(self.actionsModel)
        delegate = BorderItemDelegate(self.treeWidget, MyBorderRole) 
        self.treeWidget.setItemDelegate(delegate)
        self.connect(self.simulator, SIGNAL("startPlayAction(int)"), self._onStartPlayAction)
        self.connect(self.simulator, SIGNAL("endSimulation()"), self._onEndSimulation)
        
        self.btnPlayAction = QToolButton()
        self.btnPlayAction.setText('Play')
        self.connect(self.btnPlayAction, SIGNAL("clicked()"), self._onPlayActionClicked)    
        
        self.btnRemoveAction = QToolButton()
        self.btnRemoveAction.setText('-')
        self.connect(self.btnRemoveAction, SIGNAL("clicked()"), self._onRemoveActionClicked)
        
        self.btnClearAction = QToolButton()
        self.btnClearAction.setText('Clear all')
        self.connect(self.btnClearAction, SIGNAL("clicked()"), self._onClearActionClicked)    
        
    def _onUrlGo(self):
        url = QString(self.urlBar.text())
        if url.indexOf('http', 0) == -1:
            url = 'http://' + url
            self.urlBar.setText(url)
        self.simulator.load(url)
        if self.simulator.logger.isEnabled():
            self.actionsModel.insertRow(VisitAction(url))
        
    def _onPickerClicked(self):
        self.simulator.togglePicker()
        
    def _onRecordClicked(self, checked):
        self.simulator.logger.setEnable(checked)
        
    def _onRemoveActionClicked(self):
        self.actionsModel.removeRows(self.treeWidget.currentIndex().row())
        
    def _onClearActionClicked(self):
        self.actionsModel.removeAllRows()     
        
    def _onPlayActionClicked(self):
        self.simulator.play(self.actionsModel.actions)
    
    def _onLoadingPage(self):
        self.loadingLabel.show()  
        
    def _onPageLoaded(self):
        self.loadingLabel.hide()
        
    def _onUrlChanged(self, url):
        self.urlBar.setText(url.toString())
        
    def _onEndSimulation(self):
        self.treeWidget.setCurrentIndex(QModelIndex())    
        self.statusBar().showMessage("Simulation ended.", 2000)
        
    def _onPathPicked(self, pickedData):
        self.pathLabel.setText(pickedData.selector)
        
    def _onNewAssertionClicked(self):
        self.openAssertionDlg(self.simulator.picker.pickedData)
        
    def _onSaveActionsClicked(self):
        fname = QFileDialog.getSaveFileName(self, "Save recorded actions", QString(""), "Action XML files (*.xml)")
        if self.actionsModel.saveToXml(fname): 
            self.statusBar().showMessage("Recorded actions saved to file %s" % fname, 2000) 
            
    def _onOpenActionsClicked(self):
        fname = QFileDialog.getOpenFileName(self, "Choose a session file", QString(""), "Action XML files (*.xml)")
        if self.actionsModel.loadFromXml(fname): 
            self.statusBar().showMessage("Opened file %s" % fname, 2000) 
    
    def _onStartPlayAction(self, index):
        self.treeWidget.setCurrentIndex(self.actionsModel.index(index, 0, QModelIndex()))
        
    def buildActions(self):
        pickerAction = Gui.createAction(self, "Invert", self._onPickerClicked, "Ctrl+P", "pipette", "Toggle picker", True, "toggled(bool)")
        recordAction = Gui.createAction(self, "Record", self._onRecordClicked, "Ctrl+R", "record", "Toggle recording", True, "toggled(bool)")
        newAssertionAction = Gui.createAction(self, "New assertion", self._onNewAssertionClicked, "Ctrl+A", "eye", "New assertion")
        saveAction = Gui.createAction(self, "Save", self._onSaveActionsClicked, "Ctrl+S", "disk", "Save recorded session")
        openAction = Gui.createAction(self, "Open", self._onOpenActionsClicked, "Ctrl+O", "folder", "Open saved session")
        mainToolbar = QToolBar("Main actions")
        mainToolbar.addActions((pickerAction, recordAction, newAssertionAction, saveAction, openAction))
        self.addToolBar(Qt.LeftToolBarArea, mainToolbar)
        
if __name__ == '__main__':
    pass


app = QApplication(sys.argv)
form = MainWindow() 
form.show() 
app.exec_()