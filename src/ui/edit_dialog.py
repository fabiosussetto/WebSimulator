from PyQt4.QtCore import *
from PyQt4.QtGui import *
from simulation import *

class EditDlg(QDialog):

    def __init__(self, action, actionsModel, modelIndex, parent=None):
        super(EditDlg, self).__init__(parent)
        self.parent = parent
        self.data = {}
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.actionsModel = actionsModel
        self.action = action
        self.modelIndex = modelIndex
        
        panel = QWidget();
        
        self._buildForm(panel)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Close)
        
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(panel)
        self.vLayout.addWidget(buttonBox)

        self.setLayout(self.vLayout)
        
        self.connect(buttonBox.button(QDialogButtonBox.Apply), SIGNAL("clicked()"), self.apply)
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        
        self.setWindowTitle("Edit action")
        self.setMinimumSize(500, 100)

    def apply(self):
        self.action.url = self.urlEdit.text()
        self.actionsModel.refresh() 
        QDialog.accept(self)    
        
    def _buildForm(self, parent):
        self.actionForm = QFormLayout(parent)
        self.actionForm.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.urlEdit = QLineEdit()
        self.urlEdit.setText(self.action.url)
        self.actionForm.addRow("Url to visit:", self.urlEdit)
        
