'''
Created on Aug 22, 2011

@author: fabio
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.etree.ElementTree as Et
from xml.etree.ElementTree import tostring
from simulation.exceptions import *
from abc import *

class Action(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self):
        pass
    
    def getDescription(self):
        return 'Unknow action'    
    
    @abstractmethod    
    def execute(self, simulator):
        pass
    
    @abstractmethod    
    def fromXML(self, xmlNode):
        pass
    
    @abstractmethod    
    def toXML(self):
        element = Et.Element("action")
        return element
    
class UserAction(Action):
    
    __metaclass__ = ABCMeta
    
    selector = None
    value = None
    label = None
    error = False
    description = None

    def __init__(self, selector=None, value=None, label=None, xmlNode=None):
        super(UserAction, self).__init__()
        if xmlNode is None:
            self.description = "User action"
            self.selector = unicode(selector)
            self.value = unicode(value)
            self.label = unicode(label)
        else:
            self.fromXML(xmlNode)
            
    def reset(self):
        self.error = False        

    @abstractmethod
    def fromXML(self, node):
        selectorNode = node.find("selector")
        contentNode = node.find("content")
        if selectorNode is not None:
            self.selector = selectorNode.get("path")
        if contentNode is not None:
            self.value = contentNode.get("value")
        self.label = unicode(node.get("label"))
    
    @abstractmethod        
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", self.__class__.__name__.replace('Action', ''))
        return element
            
class AssertAction(Action):
    
    __metaclass__ = ABCMeta
    
    selector = None
    value = None
    passed = None
    description = None
    
    def __init__(self, selector=None, value=None, xmlNode=None):
        super(AssertAction, self).__init__()
        if xmlNode is None:
            self.description = "Assertion"
            self.selector = unicode(selector)
            self.value = unicode(value)
        else:
            self.fromXML(xmlNode)
        self.passed = None   
        
    def reset(self):
        self.passed = None      
        
    @abstractmethod
    def fromXML(self, node):
        pass
    
    @abstractmethod        
    def toXML(self):
        element = Et.Element("assertion")
        element.set("type", self.__class__.__name__.replace('Action', ''))
        return element