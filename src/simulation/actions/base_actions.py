'''
Created on Aug 22, 2011

@author: fabio
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.etree.ElementTree as Et
from xml.etree.ElementTree import tostring

class Action(object):
    
    def __init__(self):
        self.value = None
        self.selector = None
        self.type = None
        
    def toXML(self):
        element = Et.Element("action")
        return element
    
    def fromXML(node):
        tag = node.tag
        if tag == "useraction":
            type = node.get("type")
            if type == "fill":
                selector = node.find("selector")
                content = node.find("content")
                return FillAction(selector.get("path"), content.get("value"), node.get("label"))
            elif type == "clicklink":
                selector = node.find("selector")
                return ClickLinkAction(selector.get("path"), node.get("text"))
            elif type == "clickbutton":
                selector = node.find("selector")
                return ClickButtonAction(selector.get("path"), node.get("text"))
        elif tag == "assertion":
            type = node.get("type")
            if type == "content":
                selector = node.find("selector")
                content = node.find("content")
                return AssertContentAction(selector.get("path"), content.get("value"))
        else:
            raise Exception("Invalid tag type")
    
    fromXML = staticmethod(fromXML)


class UserAction(Action):

    def __init__(self, selector, value=None, label=None):
        super(UserAction, self).__init__()
        self.description = "User action"
        self.selector = unicode(selector)
        self.value = unicode(None)
        self.label = unicode(None)
        if value:
            self.value = unicode(value)
        if label:
            self.label = unicode(label)
            self.description += ' for ' + self.label
            
class AssertAction(Action):
    
    def __init__(self, selector, value):
        super(AssertAction, self).__init__()
        self.description = 'Assert'
        self.selector = unicode(selector)
        self.value = unicode(value)
        self.passed = None            

class FillAction(UserAction):
    
    def __init__(self, selector, value, label=""):
        super(FillAction, self).__init__(selector, value, label)
        label = unicode(label)
        self.description = "Fill input for '%s'" % label
        
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", "fill")
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"value": self.value})
        return element
        
class ClickLinkAction(UserAction):
    
    def __init__(self, selector, text=""):
        super(ClickLinkAction, self).__init__(selector)
        self.text = unicode(text)
        self.description = "Click link '%s'" % self.text
         
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", "clicklink")
        element.set("text", self.text)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element
        
class ClickButtonAction(UserAction):
    
    def __init__(self, selector, text=""):
        super(ClickButtonAction, self).__init__(selector)
        self.text = unicode(text)
        self.description = "Click button '%s'" % self.text
        
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", "clickbutton")
        element.set("text", self.text)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element 
            
class AssertContentAction(AssertAction):
    
    def __init__(self, selector, value):
        super(AssertContentAction, self).__init__(selector, value)
        self.description = 'Assert contain'
        
    def toXML(self):
        element = Et.Element("assertion")
        element.set("type", "content")
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"value": self.value})
        return element
        
class AssertPresenceAction(Action):
    
    def __init__(self, selector, checkVisibility=False):
        super(AssertPresenceAction, self).__init__()
        self.description = 'Assert presence'
        self.selector = selector
        self.checkVisibility = checkVisibility

        
class ActionContainer(object):   
    
    def __init__(self):
        self.dirty = False
        self.actions = {}

    def action(self, identity):
        return self.actions.get(identity)

    def addAction(self, action):
        self.actions[id(action)] = action
        self.dirty = True

    def removeAction(self, action):
        del self.actions[id(action)]
        del action
        self.dirty = True

    def __len__(self):
        return len(self.actions)

    def __iter__(self):
        for action in self.actions.values():
            yield action

            
class ActionListModel(QAbstractListModel):

    def __init__(self):
        super(ActionListModel, self).__init__()
        self.dirty = False
        self.actions = []

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.actions)):
            return QVariant()
        action = self.actions[index.row()]
        #column = index.column()
        if role == Qt.DisplayRole:
            return QVariant(action.type)            
        return QVariant()

    def rowCount(self, index=QModelIndex()):
        return len(self.actions)
    
    def columnCount(self, index=QModelIndex()):
        return 1
    
    def insertRows(self, action, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        self.actions.insert(position, action)
        self.endInsertRows()
        self.dirty = True
        return True
    
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
                        
class treeModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(treeModel, self).__init__(parent)
        self.actions = []
            
        self.rootItem = TreeItem(None, None, None)
        #self.parents = {0 : self.rootItem}
        self.parents = [self.rootItem]
        self.setupModelData()

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return QVariant(item.value)
        if role == Qt.UserRole:
            if item:
                return item.value
        if role == Qt.BackgroundRole:
            if isinstance(item.action, AssertAction):
                if item.action.passed == True: 
                    return QVariant(QBrush(QColor("green")))
                elif item.action.passed == False:
                    return QVariant(QBrush(QColor("red")))

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
    
    def insertRows(self, action, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        self.actions.insert(position, action)
        self.addItem(action)
        self.endInsertRows()
        self.dirty = True
        return True
    
    def removeRows(self, position, rows=1, index=QModelIndex()): 
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1) 
        self.actions = self.actions[:position] + self.actions[position + rows:]
        self.removeItem(position) 
        self.endRemoveRows()
        self.dirty = True 
        return True
    
    def removeAllRows(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount()) 
        self.actions = []
        for position in range(0, self.rowCount()):
            self.removeItem(position) 
        self.endRemoveRows()
        self.dirty = True 
        return True
        
    
    def setupModelData(self):
        for action in self.actions:
            self.addItem(action)
    
    def addItem(self, action):
        newparent = TreeItem(TreeItem.MAIN_NODE, action.description, self.rootItem, action)
        newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Selector: %s" % action.selector, newparent))
        
        actionClass = action.__class__.__name__
        if actionClass == "AssertContentAction":
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Value: %s" % action.value, newparent))
        elif actionClass == "AssertPresenceAction":
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Check visibility: %s" % action.checkVisibility, newparent))
        elif actionClass == "FillAction":
            newparent.appendChild(TreeItem(TreeItem.DETAIL_NODE, "Value: %s" % action.value, newparent))    
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
            loadedActions.append(Action.fromXML(actionNode))
                
        self.removeAllRows()                
        self.actions = loadedActions
        self.setupModelData()
        self.reset()
    
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
            
