from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AssertionDlg(QDialog):

    def __init__(self, actionsModel, pickedData, parent=None):
        super(AssertionDlg, self).__init__(parent)
        self.data = {}
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.actionsModel = actionsModel
        self.pickedData = pickedData

        self.assertionTypeSelect = QComboBox()
        self.assertionTypeSelect.addItems(["Element contains", "Element presence"])
        
        self.page1 = QWidget()
        self.page2 = QWidget()
        
        self._buildContentAssertionForm(self.page1)
        self._buildPresenceAssertionForm(self.page2)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Close)
        
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.page1) 
        self.stackedWidget.addWidget(self.page2) 
        
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.assertionTypeSelect)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        self.vLayout.addWidget(separator)
        self.vLayout.addWidget(self.stackedWidget)
        self.vLayout.addWidget(buttonBox)

        self.setLayout(self.vLayout)
        
        self.assertionTypeSelect.currentIndexChanged.connect(self.comboboxChanged)

        self.connect(buttonBox.button(QDialogButtonBox.Apply), SIGNAL("clicked()"), self.apply)
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.setWindowTitle("Set assertion")
        self.setMinimumSize(500, 100)

    def apply(self):
        assertionType = self.assertionTypeSelect.currentIndex()
        if assertionType == 0:
            selector = unicode(self.selectorEdit.text())
            content = unicode(self.contentEdit.text())
            action = actions.AssertContentAction(selector, content)
        elif assertionType == 1:
            selector = unicode(self.selectorEdit.text())
            visibility = unicode(self.visibilityCheck.isChecked())
            action = actions.AssertPresenceAction(selector, visibility)
        
        self.actionsModel.insertRows(action, self.actionsModel.rowCount())
        QDialog.accept(self)    
        
    def comboboxChanged(self, index):
        self.stackedWidget.setCurrentIndex(index)
        #self.apply_but.setEnabled(index != 0)    
        
    def _buildContentAssertionForm(self, page):
        self.contentAssertionForm = QFormLayout(page)
        self.contentAssertionForm.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.contentEdit = QLineEdit(self.pickedData.value)
        self.selectorEdit = QLineEdit(self.pickedData.selector)
        
        #elementTypeDescLabel = QLabel("Element type:")
        #elementTypeLabel = QLabel(self.pickedData.elementType)
        
        self.contentAssertionForm.addRow("Picked selector", self.selectorEdit)
        self.contentAssertionForm.addRow("Element should contain", self.contentEdit)
        
    def _buildPresenceAssertionForm(self, page):
        self.contentPresenceForm = QFormLayout(page)
        self.contentPresenceForm .setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.selectorEdit = QLineEdit(self.pickedData.selector)
        self.visibilityCheck = QCheckBox()
        self.contentPresenceForm.addRow("Picked selector", self.selectorEdit)
        self.contentPresenceForm.addRow("Check for visibility", self.visibilityCheck)