'''
Created on Aug 22, 2011

@author: fabio
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.etree.ElementTree as Et
from xml.etree.ElementTree import tostring
from simulation.exceptions import *

class Action(object):
    
    def __init__(self):
        self.value = None
        self.selector = None
        self.type = None
        
    def toXML(self):
        element = Et.Element("action")
        return element
    
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
