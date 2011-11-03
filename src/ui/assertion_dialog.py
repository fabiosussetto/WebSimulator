from PyQt4.QtCore import *
from PyQt4.QtGui import *
from simulation import *

class AssertionDlg(QDialog):

    def __init__(self, actionsModel, pickedData, parent=None):
        super(AssertionDlg, self).__init__(parent)
        self.parent = parent
        self.data = {}
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.actionsModel = actionsModel
        self.pickedData = pickedData

        self.assertionTypeSelect = QComboBox()
        self.assertionTypeSelect.addItems(["Element contains", "Element presence", "Element count"])
        
        self.page1 = QWidget()
        self.page2 = QWidget()
        self.page3 = QWidget()
        
        self._buildContentAssertionForm(self.page1)
        self._buildPresenceAssertionForm(self.page2)
        self._buildCountAssertionForm(self.page3)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Close)
        
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.page1) 
        self.stackedWidget.addWidget(self.page2) 
        self.stackedWidget.addWidget(self.page3) 
        
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
        
        self.connect(self.parent.simulator.picker, SIGNAL("pathPicked(PyQt_PyObject)"), self._onPathPicked)
        
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
        elif assertionType == 2:
            selector = self.countSelectorEdit.text()
            count = self.countEdit.value()
            context = self.countContextEdit.text()
            action = actions.AssertCountAction(selector, count, context)    
        
        self.actionsModel.insertRow(action)
        self.parent.simulator.logger.setEnable(True)
        QDialog.accept(self)    
        
    def comboboxChanged(self, index):
        self.stackedWidget.setCurrentIndex(index)
        
    def _buildContentAssertionForm(self, page):
        self.contentAssertionForm = QFormLayout(page)
        self.contentAssertionForm.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.contentEdit = QLineEdit()
        self.selectorEdit = QLineEdit()
        
        self.btnPick = QToolButton()
        self.btnPick.setText('Pick')
        self.connect(self.btnPick, SIGNAL("clicked()"), self._onPickClicked)    
                
        selectorPicker = QHBoxLayout()
        selectorPicker.addWidget(self.selectorEdit)
        selectorPicker.addWidget(self.btnPick)
        
        self.contentAssertionForm.addRow("Picked selector", selectorPicker)
        self.contentAssertionForm.addRow("Element should contain", self.contentEdit)
        
    def _buildPresenceAssertionForm(self, page):
        self.contentPresenceForm = QFormLayout(page)
        self.contentPresenceForm .setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        #self.selectorEdit = QLineEdit(self.pickedData.selector)
        #self.selectorEdit = QLineEdit()
        #self.visibilityCheck = QCheckBox()
        #self.contentPresenceForm.addRow("Picked selector", self.selectorEdit)
        #self.contentPresenceForm.addRow("Check for visibility", self.visibilityCheck)
        
    def _buildCountAssertionForm(self, page):
        self.countAssertionForm = QFormLayout(page)
        self.countAssertionForm.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
       
        self.countSelectorEdit = QLineEdit()
        self.countContextEdit = QLineEdit()
        self.countEdit = QSpinBox()
        self.countEdit.setValue(1)
        
        self.btnCountPathPick = QToolButton()
        self.btnCountPathPick.setText('Pick')
        self.connect(self.btnCountPathPick, SIGNAL("clicked()"), self._onBtnCountPathClicked)    
        
        self.btnCountContextPick = QToolButton()
        self.btnCountContextPick.setText('Pick')
        self.connect(self.btnCountContextPick, SIGNAL("clicked()"), self._onBtnCountContextClicked)    
                
        selectorPicker = QHBoxLayout()
        selectorPicker.addWidget(self.countSelectorEdit)
        selectorPicker.addWidget(self.btnCountPathPick)
        
        contextPicker = QHBoxLayout()
        contextPicker.addWidget(self.countContextEdit)
        contextPicker.addWidget(self.btnCountContextPick)
        
        self.countAssertionForm.addRow("Element selector", selectorPicker)
        self.countAssertionForm.addRow("Element count", self.countEdit)    
        self.countAssertionForm.addRow("Context selector", contextPicker)
        
    def _onPickClicked(self):
        self._pathTarget = self.selectorEdit
        self._commonPicked()
        self.hide()
        
    def _onBtnCountPathClicked(self):
        self._pathTarget = self.countSelectorEdit
        self._commonPicked()
        self.hide()
    
    def _onBtnCountContextClicked(self):
        self._pathTarget = self.countContextEdit
        self._commonPicked()
        self.hide()
        
    def _commonPicked(self):
        self.parent.simulator.picker.setEnable(True)
        self.parent.simulator.logger.setEnable(False)    
        
    # Called when user finish to select the element    
    def _onPathPicked(self, pickedData):
        self.show()
        self._pathTarget.setText(pickedData.selector)
        self.contentEdit.setText(pickedData.value)
        self.parent.simulator.picker.setEnable(False)
