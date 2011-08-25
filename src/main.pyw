'''
Created on May 2, 2011

@author: fabio
'''

import sys
import time
import simulation
from recording import actions, picker
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from test_cases import wp3testcase, wp2testcase
import qrc_resources
import ui

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        #self.model = actions.ActionListModel()
        
        self.actionsModel = actions.treeModel()
        self.simulator = simulation.Simulator(self.actionsModel)
        
        self.mainSplitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.mainSplitter)
        splitterLeft = QWidget()
        splitterRight = QWidget()
        self.mainSplitter.addWidget(splitterLeft)
        self.mainSplitter.addWidget(splitterRight)
        
        self.urlBar = QLineEdit()
        self.urlGo = QPushButton("Vai")
        self.btnSimulate = QPushButton("Run test")
        self.connect(self.btnSimulate, SIGNAL("clicked()"), self._onSimulateClicked)
        
        self.simulator.createView()
        self.browser = self.simulator.getWidget()
        self.browser.setMinimumWidth(900)
        
        self.connect(self.simulator, SIGNAL("loadingPage()"), self._onLoadingPage)
        self.connect(self.simulator, SIGNAL("pageLoaded()"), self._onPageLoaded)
        self.connect(self.simulator.picker, SIGNAL("pathPicked(PyQt_PyObject)"), self._onPathPicked)
        
        self.browser.show()
        
        self.loadingLabel = QLabel('Loading page ...')
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        self.loadingLabel.hide()
        
        self.pathLabel = QLabel()
        #self.pathLabel.hide()
        
        urlLayout = QHBoxLayout()
        urlLayout.addWidget(self.urlBar)
        urlLayout.addWidget(self.urlGo)
        
        self.treeWidget = QTreeView()
        self.treeWidget.setModel(self.actionsModel)
        
        self.btnRemoveAction = QToolButton()
        self.btnRemoveAction.setText('-')
        self.connect(self.btnRemoveAction, SIGNAL("clicked()"), self._onRemoveActionClicked)

        self.btnPlayAction = QToolButton()
        self.btnPlayAction.setText('Play')
        self.connect(self.btnPlayAction, SIGNAL("clicked()"), self._onPlayActionClicked)
        
        rightLayout = QVBoxLayout(splitterRight)
        #self.actionsToolbar = QToolBar()
        #self.actionsToolbar.addAction(QAction(QIcon(":/pipette.png"), QString("Picker"), self))
        #self.actionsToolbar.addAction(QAction(QString("Bar"), self))
        #rightLayout.addWidget(self.actionsToolbar)
        rightLayout.addWidget(self.treeWidget)
        rightLayout.addWidget(self.btnRemoveAction)
        rightLayout.addWidget(self.btnPlayAction)
        
        
        layout = QVBoxLayout(splitterLeft)
        layout.addLayout(urlLayout)
        layout.addWidget(self.browser)
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.pathLabel)
        #layout.addWidget(self.btnSimulate)
        
        self.setWindowTitle("Test Webkit")
        self.setMinimumSize(1200, 600)
        
        #editMenu = self.menuBar().addMenu("Edit")
        #editToolbar = self.addToolBar("Edit")
        self.buildActions()
        
        self.simulator.load_js()
        self.simulator.load('http://wptesi/wp_3-1-3/wp-admin')
        
    def openAssertionDlg(self, pickedData):
        self.assertionDlg = ui.AssertionDlg(self.actionsModel, pickedData, self)
        if self.assertionDlg.exec_():
            pass
            #data = self.assertionDlg.data
        
    def _onSimulateClicked(self):
        test_case = wp3testcase.Wp3TestCase(self.simulator)
        test_case.run()
        
        #test_case = wp2testcase.Wp2TestCase(self.simulator)
        #test_case.run()
        
    def _onPickerClicked(self):
        self.simulator.togglePicker()
        
    def _onRecordClicked(self, checked):
        self.simulator.logger.setEnable(checked)
        
    def _onRemoveActionClicked(self):
        self.actionsModel.removeRows(self.treeWidget.currentIndex().row())    
        
    def _onPlayActionClicked(self):
        self.simulator.play(self.actionsModel.actions)
    
    def _onLoadingPage(self):
        self.loadingLabel.show()  
        
    def _onPageLoaded(self):
        self.loadingLabel.hide()
        
    def _onPathPicked(self, pickedData):
        self.pathLabel.setText(pickedData.selector)
        #self.openAssertionDlg(pickedData)
        
    def _onNewAssertionClicked(self):
        self.openAssertionDlg(self.simulator.picker.pickedData)
        
    def _onSaveActionsClicked(self):
        fname = QFileDialog.getSaveFileName(self, "Save recorded actions", QString(""), "Action XML files (*.xml)")
        if self.actionsModel.saveToXml(fname): 
            self.statusBar().showMessage("Recorded actions saved to file %s" % fname, 2000)   
        
    def buildActions(self):
        pickerAction = self.createAction("Invert", self._onPickerClicked, "Ctrl+P", "pipette", "Toggle picker", True, "toggled(bool)")
        recordAction = self.createAction("Record", self._onRecordClicked, "Ctrl+R", "record", "Toggle recording", True, "toggled(bool)")
        newAssertionAction = self.createAction("New assertion", self._onNewAssertionClicked, "Ctrl+A", "eye", "New assertion")
        saveAction = self.createAction("Save", self._onSaveActionsClicked, "Ctrl+S", "disk", "Save recorded session")
        mainToolbar = self.addToolBar("Recording")
        mainToolbar.addActions((pickerAction, recordAction, newAssertionAction, saveAction))
        
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self) 
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon)) 
        if shortcut is not None:
            action.setShortcut(shortcut) 
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip) 
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot) 
        if checkable:
            action.setCheckable(True)
        return action    
        
        
if __name__ == '__main__':
    pass


app = QApplication(sys.argv)
form = MainWindow() 
form.show() 
app.exec_()