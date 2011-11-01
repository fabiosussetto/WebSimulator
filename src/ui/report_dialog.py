from PyQt4.QtCore import *
from PyQt4.QtGui import *
from simulation import *

class ReportDlg(QDialog):

    def __init__(self, parent=None):
        super(ReportDlg, self).__init__(parent)
        self.parent = parent
        
        self.setWindowTitle("Test execution report")
        self.setMinimumSize(400, 100)

    def apply(self):        
        QDialog.accept(self)
        