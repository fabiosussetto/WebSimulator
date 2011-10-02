from PyQt4.QtCore import QObject, pyqtSignature, pyqtSignal, pyqtSlot

class Picker(QObject): 
    
    pathPicked = pyqtSignal("PyQt_PyObject")
    
    enabled = False
    
    currentPath = None
    
    pickedData = None
    
    def toggleEnable(self):
        self.enabled = not self.enabled
    
    def setEnable(self, enable):
        self.enabled = enable
    
    @pyqtSlot(result="bool")    
    def isEnabled(self):
        return self.enabled
    
    @pyqtSignature("QString, QString, QString")
    def setPath(self, selector, elementType, value=None):
        self.currentPath = selector
        self.pickedData = PickedData(selector, elementType, value)
        self.pathPicked.emit(self.pickedData)
        

class PickedData(object):

    def __init__(self, selector, elementType, value=None):
        self.selector = selector
        self.elementType = elementType
        self.value = value.trimmed()        
