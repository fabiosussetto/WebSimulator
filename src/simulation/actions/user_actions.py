from base_actions import UserAction
import xml.etree.ElementTree as Et
#from xml.etree.ElementTree import tostring
from simulation.exceptions import *
from PyQt4.QtCore import QEvent, Qt
from PyQt4.Qt import QApplication
from PyQt4.QtGui import QMouseEvent
from PyQt4.QtTest import *

class VisitAction(UserAction):
    
    def __init__(self, url=None, xmlNode=None):
        if xmlNode is None:
            self.url = unicode(url)
        else:
            self.fromXML(xmlNode)
        self.description = "Visit '%s'" % self.url
        
    def execute(self, simulator):
        simulator.load(self.url)
        
    def fromXML(self, node):
        super(VisitAction, self).fromXML(node)
        urlNode = node.find("url")    
        self.url = unicode(urlNode.get('value'))
        
    def toXML(self):
        element = super(VisitAction, self).toXML()
        element.set("label", self.description)
        Et.SubElement(element, "url", {"value": self.url})
        return element
            
class FillAction(UserAction):
    
    def __init__(self, selector=None, value=None, label="", xmlNode=None):
        super(FillAction, self).__init__(selector, value, label, xmlNode)
        self.description = "Fill input for '%s'" % self.label
        
    def execute(self, simulator):
        self._execute_native(simulator)
        #self._execute_js(simulator)
        
    def fromXML(self, node):
        super(FillAction, self).fromXML(node)
        
    def toXML(self):
        element = super(FillAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"value": self.value})
        return element
    
    def _execute_js(self, simulator):
        escaped_value = self.value.replace("'", "\\'")
        
        jscode = "%s.smartSelector.select('%s').val('%s');" % (simulator.jQueryAlias, self.selector, escaped_value)
        simulator.runjs(jscode)
    
    def _execute_native(self, simulator):
        where = simulator.getElementPosition(self.selector)
        jscode = "%s.smartSelector.select('%s').val('');" % (simulator.jQueryAlias, self.selector)
        simulator.runjs(jscode)
        QTest.mouseClick(simulator.webview, Qt.LeftButton, Qt.NoModifier, where)
        for c in self.value:
            QTest.keyEvent(QTest.Click, simulator.webview, c)
        
class ClickLinkAction(UserAction):
    
    def __init__(self, selector=None, label=None, xmlNode=None):
        super(ClickLinkAction, self).__init__(selector, None, label, xmlNode)
        self.description = "Click link '%s'" % self.label
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            self.error = True
            raise DomElementNotFound(self.selector)
        self._execute_native(simulator)
        #self._execute_js(simulator)
        return simulator.wait_load()
    
    def fromXML(self, node):
        super(ClickLinkAction, self).fromXML(node)
         
    def toXML(self):
        element = super(ClickLinkAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element
    
    def _execute_js(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        jscode = "%s.smartSelector.select('%s').simulate('click');" % (simulator.jQueryAlias, self.selector)
        simulator.runjs(jscode)
    
    def _execute_native(self, simulator):
        where = simulator.getElementPosition(self.selector)
        pageGeometry = simulator.webframe.geometry()
        if not pageGeometry.contains(where):
            offset = where.y() - pageGeometry.height();
            simulator.webframe.scroll(0, offset + 10)
            print where.y()
            print pageGeometry.height()
            where.setY(where.y() - offset - 10)
        QTest.mouseMove(simulator.webview, where)
        QTest.mouseClick(simulator.webview, Qt.LeftButton, Qt.NoModifier, where)
        
class ClickButtonAction(UserAction):
    
    def __init__(self, selector=None, label=None, xmlNode=None):
        super(ClickButtonAction, self).__init__(selector, None, label, xmlNode)
        self.description = "Click button '%s'" % self.label
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        jscode = "%s.smartSelector.select('%s').simulate('click');" % (simulator.jQueryAlias, self.selector)
        simulator.runjs(jscode)
        return simulator.wait_load()
    
    def fromXML(self, node):
        super(ClickButtonAction, self).fromXML(node)
    
    def toXML(self):
        element = super(ClickButtonAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element 
    
class SelectAction(UserAction):
    
    def __init__(self, selector=None, value=None, label=None, displayOption=None, xmlNode=None):
        super(SelectAction, self).__init__(selector, value, label, xmlNode)
        if xmlNode is None:
            self.displayOption = unicode(displayOption)
        self.description = "Select option '%s' for '%s'" % (self.displayOption, self.label)
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        if not simulator.assertExists("%s > option[value=%s]" % (self.selector, self.value)):
            raise Exception("Could not find an option with value '%s' for select at '%s'" % (self.value, self.selector))
            
        escaped_value = self.value.replace("'", "\\'")    
        jscode = "%s('%s').val('%s');" % (simulator.jQueryAlias, self.selector, escaped_value)
        
        simulator.runjs(jscode)
    
    def fromXML(self, node):
        super(SelectAction, self).fromXML(node)
        self.displayOption = unicode(node.find("content").get('display'));
    
    def toXML(self):
        element = super(SelectAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"display": self.displayOption, "value": self.value})
        return element
