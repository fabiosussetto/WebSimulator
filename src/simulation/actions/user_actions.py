from base_actions import UserAction
import xml.etree.ElementTree as Et
#from xml.etree.ElementTree import tostring
from simulation.exceptions import *

class VisitAction(UserAction):
    
    def __init__(self, url):
        self.url = unicode(url)
        self.description = "Visit '%s'" % url
        
    def execute(self, simulator):
        simulator.load(self.url)
        
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", "visit")
        element.set("label", self.description)
        Et.SubElement(element, "url", {"value": self.url})
        return element
            
class FillAction(UserAction):
    
    def __init__(self, selector, value, label=""):
        super(FillAction, self).__init__(selector, value, label)
        label = unicode(label)
        self.description = "Fill input for '%s'" % label
        
    def execute(self, simulator):
        """Fill an input text with a string value using a jQuery selector."""
        escaped_value = self.value.replace("'", "\\'")
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        #if assert_visible and not self.assertVisible(selector):
        #raise DomElementNotVisible(selector)
            
        jscode = "%s('%s').val('%s');" % (simulator.jslib, self.selector, escaped_value)
        simulator.runjs(jscode)
        
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
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        jscode = "%s('%s').simulate('click');" % (simulator.jslib, self.selector)
        simulator.runjs(jscode)
        return simulator.wait_load()
         
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
        
    def execute(self, simulator):
        if not simulator.assertExists(self.selector):
            raise DomElementNotFound(self.selector)
        
        jscode = "%s('%s').simulate('click');" % (simulator.jslib, self.selector)
        simulator.runjs(jscode)
        return simulator.wait_load()
    
    def toXML(self):
        element = Et.Element("useraction")
        element.set("type", "clickbutton")
        element.set("text", self.text)
        Et.SubElement(element, "selector", {"path": self.selector})
        return element 
