from base_actions import UserAction
import xml.etree.ElementTree as Et
#from xml.etree.ElementTree import tostring
from simulation.exceptions import *

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
        """Fill an input text with a string value using a jQuery selector."""
        escaped_value = self.value.replace("'", "\\'")
        if not simulator.assertExists(self.selector):
            self.error = True
            raise DomElementNotFound(self.selector)
        
        #if assert_visible and not self.assertVisible(selector):
        #raise DomElementNotVisible(selector)
            
        jscode = "%s('%s').val('%s');" % (simulator.jQueryAlias, self.selector, escaped_value)
        simulator.runjs(jscode)
        
    def fromXML(self, node):
        super(FillAction, self).fromXML(node)
        
    def toXML(self):
        element = super(FillAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"value": self.value})
        return element
        
class ClickLinkAction(UserAction):
    
    def __init__(self, selector=None, label=None, xmlNode=None):
        super(ClickLinkAction, self).__init__(selector, label, None, xmlNode)
        self.description = "Click link '%s'" % self.label
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        jscode = "%s('%s').simulate('click');" % (simulator.jQueryAlias, self.selector)
        simulator.runjs(jscode)
        return simulator.wait_load()
    
    def fromXML(self, node):
        super(ClickLinkAction, self).fromXML(node)
         
    def toXML(self):
        element = super(ClickLinkAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element
        
class ClickButtonAction(UserAction):
    
    def __init__(self, selector=None, label=None, xmlNode=None):
        super(ClickButtonAction, self).__init__(selector, label, None, xmlNode)
        self.description = "Click button '%s'" % self.label
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        jscode = "%s('%s').simulate('click');" % (simulator.jQueryAlias, self.selector)
        simulator.runjs(jscode)
        return simulator.wait_load()
    
    def fromXML(self, node):
        super(ClickButtonAction, self).fromXML(node)
    
    def toXML(self):
        element = super(ClickButtonAction, self).toXML()
        element.set("label", self.label)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element 
