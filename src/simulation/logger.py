from PyQt4.QtCore import QObject, pyqtSignature
import actions

class Logger(QObject): 
    
    def __init__(self):
        super(Logger, self).__init__()
        self.enabled = False
    
    def setEnable(self, enable):
        self.enabled = enable
    
    def setModel(self, model):
        self.model = model
        
    def _recordAction(self, action):
        if self.enabled:
            self.model.insertRows(action, self.model.rowCount())
    
    @pyqtSignature("QString, QString, QString")
    def fill(self, path, value, label=None):
        self._recordAction(actions.FillAction(path, value, label))
    
    @pyqtSignature("QString, QString")
    def checkbox(self, path, value):
        print "%s : %s" % (path, value)
    
    @pyqtSignature("QString, QString")
    def link(self, path, text=""):
        self._recordAction(actions.ClickLinkAction(path, text))
        
    @pyqtSignature("QString, QString")
    def submit(self, path, text=""):
        self._recordAction(actions.ClickButtonAction(path, text))