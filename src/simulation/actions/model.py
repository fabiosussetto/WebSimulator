from PyQt4.QtCore import *
from PyQt4.QtGui import *

import xml.etree.ElementTree as Et
from xml.etree.ElementTree import tostring
#from base_actions import *
from user_actions import *
from assertions import *
from utilities.generic import * 
from simulation.actions import user_actions, assertions

class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    
    MAIN_NODE = 0
    DETAIL_NODE = 1
    
    def __init__(self, type, value, parentItem, action = None):
        self.parentItem = parentItem
        self.childItems = []
        self.value = value
        self.type = type
        self.action = action

    def appendChild(self, item):
        self.childItems.append(item)
        
    def removeChild(self, position):
        self.childItems = self.childItems[:position] + self.childItems[position + 1:]
        
    def removeAllChildren(self):
        del self.childItems[:]

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 1
    
    def data(self, column):
        if self.type == self.MAIN_NODE:
            return self.action
        return QVariant(self.value)

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0    
                        
class TreeModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.actions = []
            
        self.rootItem = TreeItem(None, None, None)
        self.parents = [self.rootItem]
        self.setupModelData()

    def columnCount(self, parent=None):
        return 1
    
    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        return QString("Actions:")

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return QVariant(item.value)
        if role == Qt.ToolTipRole:
            return QVariant(item.value)
        if role == Qt.UserRole:
            if item:
                return item.value
        if role == Qt.BackgroundRole:
            if isinstance(item.action, AssertAction):
                if item.action.passed == True: 
                    return QVariant(QBrush(QColor("lightgreen")))
                elif item.action.passed == False:
                    return QVariant(QBrush(QColor("red")))
            elif isinstance(item.action, UserAction):
                if item.action.error == True: 
                    return QVariant(QBrush(QColor("yellow")))
        return QVariant()


    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QModelIndex()
        
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()
    
    def insertRow(self, action, position=None):
        if not position:
            position = self.rowCount()
        self.beginInsertRows(QModelIndex(), position, position)
        if position:
            self.actions.insert(position, action)
        else:
            self.actions.append(action)
            
        self.endInsertRows()
        self.addItem(action)
        self.dirty = True
    
    def insertRows(self, action, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        self.actions.insert(position, action)
        self.addItem(action)
        self.endInsertRows()
        self.dirty = True
    
    def removeRows(self, position, rows=1, index=QModelIndex()): 
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1) 
        self.actions = self.actions[:position] + self.actions[position + rows:]
        self.removeItem(position) 
        self.endRemoveRows()
        self.dirty = True 
    
    def removeAllRows(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount()) 
        self.actions = []
        self.rootItem.removeAllChildren()
        self.endRemoveRows()
        self.dirty = True 
        
    def refresh(self):
        prevActions = self.actions
        self.reset()
        self.removeAllRows()
        self.actions = prevActions
        self.setupModelData()
        
    def resetState(self):
        for action in self.actions:
            action.reset()
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), QModelIndex(), QModelIndex())    
        
    def setupModelData(self):
        for action in self.actions:
            self.addItem(action)
    
    def addItem(self, action):
        newparent = TreeItem(TreeItem.MAIN_NODE, action.getDescription(), self.rootItem, action)
        
        if not isinstance(action, VisitAction):
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Selector: %s" % action.selector, newparent))
        
        if isinstance(action, AssertContentAction):
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Value: %s" % action.value, newparent))
        elif isinstance(action, AssertPresenceAction):
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Check visibility: %s" % action.checkVisibility, newparent))
        elif isinstance(action, FillAction):
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Value: %s" % action.value, newparent)) 
        elif isinstance(action, VisitAction):
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Url: %s" % action.url, newparent))       
        self.parents.append(newparent)
        self.rootItem.appendChild(newparent)
        
    def removeItem(self, position):
        self.rootItem.removeChild(position)
        
    def saveToXml(self, fname):
        if fname.isEmpty():
            return False
        if not fname.contains("."): fname += ".xml"
        root = Et.Element('actions')
        for action in self.actions:
            root.append(action.toXML())
        self.indent(root)
        tree = Et.ElementTree(root)
        tree.write(fname, xml_declaration=True, encoding='utf-8', method="xml")
        return True
    
    def loadFromXml(self, fname):
        #TODO: alert if changes are made to the currently recorded actions
        tree = Et.ElementTree(file=fname)
        root = tree.getroot()
        actionNodes = list(root)
        loadedActions = []
        for actionNode in actionNodes:
            loadedActions.append(self.actionFromXML(actionNode))
                
        self.removeAllRows()                
        self.actions = loadedActions
        self.setupModelData()
        self.reset()
        
    def actionFromXML(self, node):
        tag = node.tag
        type = node.get("type")
        if tag == "useraction":
            action = getattr(user_actions, type + 'Action')(xmlNode=node)
        elif tag == "assertion":
            action = getattr(assertions, type + 'Action')(xmlNode=node)
        else:
            raise Exception("Invalid tag type")
        return action 
        
    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
class BorderItemDelegate(QStyledItemDelegate):
    def __init__(self, parent, borderRole):
        super(BorderItemDelegate, self).__init__(parent)
        self.borderRole = borderRole

    def sizeHint(self, option, index):        
        size = super(BorderItemDelegate, self).sizeHint(option, index)
        pen = index.data(self.borderRole).toPyObject()
        if pen is not None:        
            width = max(pen.width(), 1)            
            size = size + QSize(2 * width, 2 * width)
        return size

    def paint(self, painter, option, index):
        item = index.internalPointer()
        if item.type == TreeItem.DETAIL_NODE:
            return super(BorderItemDelegate, self).paint(painter, option, index) 
        
        pen = QPen(QColor.fromRgb(221, 221, 221))
        pen.setWidth(0.5)
        rect = QRect(option.rect)
        if pen is not None:
            width = max(pen.width(), 1)
            option.rect.adjust(width, width, -width, -width)      

        super(BorderItemDelegate, self).paint(painter, option, index)

        if pen is not None:
            painter.save()  
            painter.setClipRect(rect, Qt.ReplaceClip);          
            painter.setPen(pen)
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())     
            painter.restore()
    