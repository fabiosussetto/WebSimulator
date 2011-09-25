from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon

class Gui(object):

    @staticmethod
    def createAction(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, parent) 
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon)) 
        if shortcut is not None:
            action.setShortcut(shortcut) 
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip) 
        if slot is not None:
            parent.connect(action, SIGNAL(signal), slot) 
        if checkable:
            action.setCheckable(True)
        return action