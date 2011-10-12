from base_actions import AssertAction
from PyQt4.QtGui import QImage, QPainter
import xml.etree.ElementTree as Et
#from xml.etree.ElementTree import tostring
from simulation.exceptions import *

class AssertContentAction(AssertAction):
    
    def __init__(self, selector=None, value=None, xmlNode=None):
        super(AssertContentAction, self).__init__(selector, value, xmlNode)
        self.description = 'Assert contain text'
        
    def execute(self, simulator):
        jscode = "_assert.contentMatch('%s', '%s');" % (self.value, self.selector)
        result = simulator.runjs(jscode)
        result = result.toBool()
        if not result:
            self.passed = False
            '''
            image = QImage(simulator.webpage.viewportSize(), QImage.Format_ARGB32)
            painter = QPainter(image)
            simulator.webframe.render(painter)
            painter.end()
            image.save("output.png")
            '''
            raise AssertException("Could not find text '%s' inside DOM element at '%s'" % (self.value, self.selector))
        else:
            self.passed = True
    
    def fromXML(self, node):
        super(AssertContentAction, self).fromXML(node)
        selectorNode = node.find("selector")
        contentNode = node.find("content")
        self.selector = selectorNode.get("path")
        self.value = contentNode.get("value")
        
    def toXML(self):
        element = super(AssertContentAction, self).toXML()
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"value": self.value})
        return element
    
class AssertCountAction(AssertAction):
    
    def __init__(self, selector=None, count=None, context=None, xmlNode=None):
        super(AssertAction, self).__init__()
        if xmlNode is None:
            self.selector = unicode(selector)
            self.count = count
            self.context = unicode(context)
        else:
            self.fromXML(xmlNode)
        self.passed = None
        self.description = 'Assert element count'
        
    def execute(self, simulator):
        jscode = "_assert.count('%s', '%s');" % (self.selector, self.context)
        result = simulator.runjs(jscode)
        result = result.toInt()[0]
        if result != self.count:
            self.passed = False
            raise AssertException("Expected %d elements for '%s', found %d" % (self.count, self.selector, result))
        else:
            self.passed = True
    
    def fromXML(self, node):
        super(AssertCountAction, self).fromXML(node)
        selectorNode = node.find("selector")
        contentNode = node.find("content")
        self.selector = selectorNode.get("path")
        self.context = selectorNode.get("context")
        self.count = contentNode.get("count")
        
    def toXML(self):
        element = super(AssertCountAction, self).toXML()
        Et.SubElement(element, "selector", {"path": self.selector, "context": self.context})
        Et.SubElement(element, "content", {"count": self.count})
        return element    
    
        
class AssertPresenceAction(AssertAction):
    
    def __init__(self, selector, checkVisibility=False):
        super(AssertPresenceAction, self).__init__()
        self.description = 'Assert presence'
        self.selector = selector
        self.checkVisibility = checkVisibility
        
        
class AssertException(Exception):
    """Error on the injected Javascript code."""