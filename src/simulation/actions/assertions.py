from base_actions import AssertAction
from PyQt4.QtGui import QImage, QPainter
import xml.etree.ElementTree as Et
#from xml.etree.ElementTree import tostring
from simulation.exceptions import *

class AssertContentAction(AssertAction):
    
    def __init__(self, selector, value):
        super(AssertContentAction, self).__init__(selector, value)
        self.description = 'Assert contain'
        
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
        
    def toXML(self):
        element = Et.Element("assertion")
        element.set("type", "content")
        Et.SubElement(element, "selector", {"path": self.selector})
        Et.SubElement(element, "content", {"value": self.value})
        return element
        
class AssertPresenceAction(AssertAction):
    
    def __init__(self, selector, checkVisibility=False):
        super(AssertPresenceAction, self).__init__()
        self.description = 'Assert presence'
        self.selector = selector
        self.checkVisibility = checkVisibility
        
        
class AssertException(Exception):
    """Error on the injected Javascript code."""