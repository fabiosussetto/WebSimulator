'''
Created on Aug 22, 2011

@author: fabio
'''
from PyQt4.QtCore import *
import xml.etree.ElementTree as Et

class Action(object):
    
    def __init__(self):
        self.value = None
        self.selector = None
        self.type = None
        
    def toXML(self):
        element = Et.Element("action")
        return element


class UserAction(Action):

    def __init__(self, description, type, selector, value=None, label=None):
        super(UserAction, self).__init__()
        self.type = type
        self.description = description
        self.selector = unicode(selector)
        self.value = unicode(None)
        self.label = unicode(None)
        if value:
            self.value = unicode(value)
        if label:
            self.label = unicode(label)
            self.description += ' for ' + self.label
            
    def play(self):
        pass
            
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", "fill")
        selector = Et.SubElement(element, "selector")
        selector.set("path", self.selector)
        content = Et.SubElement(element, "content", {"value": self.value})
        #content.set("value", self.value)
        return element
        
class AssertAction(Action):
    
    def __init__(self, selector, value):
        super(AssertAction, self).__init__()
        self.description = 'Assert'
        self.selector = selector
        self.value = value
        
    def toXML(self):
        element = Et.Element("assertion")
        element.set("type", "AssertAction")
        selector = Et.SubElement(element, "selector")
        selector.set("path", self.selector)
        content = Et.SubElement(element, "content")
        content.set("value", self.value)
        return element
            
        
class AssertContentAction(AssertAction):
    
    def __init__(self, selector, value):
        super(AssertContentAction, self).__init__(selector, value)
        self.description = 'Assert contain'
        
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
    def __init__(self, value, parentItem):
        self.parentItem = parentItem
        self.childItems = []
        self.value = value

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
        return QVariant(self.value)

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0    
                        
class treeModel(QAbstractItemModel):
    '''
    a model to display a few names, ordered by sex
    '''
    def __init__(self, parent=None):
        super(treeModel, self).__init__(parent)
        self.actions = []
            
        self.rootItem = TreeItem(None, None)
        self.parents = {0 : self.rootItem}
        self.parents = [self.rootItem]
        self.setupModelData()

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.data(index.column())
        if role == Qt.UserRole:
            if item:
                return item.value

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
    
    def setupModelData(self):
        for action in self.actions:
            self.addItem(action)
    
    def addItem(self, action):
        newparent = TreeItem(action.description, self.rootItem)
        newparent.appendChild(TreeItem("Selector: %s" % action.selector, newparent))
        
        actionClass = action.__class__.__name__
        if actionClass == "AssertContentAction":
            newparent.appendChild(TreeItem("Value: %s" % action.value, newparent))
        elif actionClass == "AssertPresenceAction":
            newparent.appendChild(TreeItem("Check visibility: %s" % action.checkVisibility, newparent))
        elif actionClass == "UserAction":
            newparent.appendChild(TreeItem("Value: %s" % action.value, newparent))    
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
            
