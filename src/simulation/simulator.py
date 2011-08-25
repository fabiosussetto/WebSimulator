'''
Created on May 31, 2011

@author: fabio
'''

import os
import time
import pyquery
import re

#from PyQt4.QtCore import pyqtSignal, SIGNAL, QUrl, QString, Qt, QObject, QEvent
#from PyQt4.QtCore import QSize, QDateTime, QPoint
#from PyQt4.QtGui import QApplication, QImage, QPainter
#from PyQt4.QtGui import QCursor, QMouseEvent, QKeyEvent
from PyQt4.QtNetwork import QNetworkCookie, QNetworkAccessManager
from PyQt4.QtNetwork import QNetworkCookieJar, QNetworkRequest, QNetworkProxy
#from PyQt4.QtWebKit import QWebPage, QWebView

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from recording import actions, picker

class Picker(QObject): 
    
    pathPicked = pyqtSignal("PyQt_PyObject")
    
    enabled = False
    
    currentPath = None
    
    pickedData = None
    
    @pyqtSignature("QString, QString, QString")
    def setPath(self, selector, elementType, value=None):
        self.currentPath = selector
        self.pickedData = picker.PickedData(selector, elementType, value)
        self.pathPicked.emit(self.pickedData)
        
class Logger(QObject): 
    
    def __init__(self):
        super(Logger, self).__init__()
        self.enabled = False
    
    def setEnable(self, enable):
        self.enabled = enable
    
    def setModel(self, model):
        self.model = model
        
    def _recordAction(self, action):
        if self.enabled:
            self.model.insertRows(action, self.model.rowCount())
    
    @pyqtSignature("QString, QString, QString")
    def content(self, path, value, label=None):
        self._recordAction(actions.UserAction("Fill input", "fill", path, value, label))
    
    @pyqtSignature("QString, QString")
    def checkbox(self, path, value):
        print "%s : %s" % (path, value)
    
    @pyqtSignature("QString")
    def link(self, path):
        self._recordAction(actions.UserAction("Click link", "link", path))
        
    @pyqtSignature("QString")
    def submit(self, path):
        self._recordAction(actions.UserAction("Submit form", "submit", path))
        

class Simulator(QObject):
    '''
    classdocs
    '''
    _jquery = 'jquery-1.6.1.js'
    _jquery_simulate = 'jquery.simulate.js'
    
    loadingPage = pyqtSignal()
    pageLoaded = pyqtSignal()
    pathPicked = pyqtSignal()

    def __init__(self, model):
        '''
        Constructor
        '''
        super(Simulator, self).__init__()
        self.webpage = QWebPage()
        #self.webpage.userAgentForUrl = 'test'
        self.webframe = self.webpage.mainFrame()
        
        self.webpage.connect(self.webpage, SIGNAL('loadFinished(bool)'), self._on_load_finished)
        self.webpage.connect(self.webpage, SIGNAL("loadStarted()"), self._on_load_started)
        
        self.jquery = open(os.path.join(os.path.dirname(__file__), "../javascript/" + self._jquery)).read()
        self.jquery_simulate = open(os.path.join(os.path.dirname(__file__), "../javascript/" + self._jquery_simulate)).read()
        self.jquery_picker = open(os.path.join(os.path.dirname(__file__), "../test/picker.js")).read()
        self.jquery_logger = open(os.path.join(os.path.dirname(__file__), "../test/logger.js")).read()
        
        self.jslib = '$'
        self._load_status = None
        
        self.picker = Picker();
        self.logger = Logger();
        self.logger.setModel(model)
        
    def createView(self):
        self.webview = QWebView()
        self.webview.setPage(self.webpage)
        
    def getWidget(self):
        return self.webview
        
    def _on_load_started(self):
        self._load_status = None
        #self.emit(SIGNAL("loadingPage"))
        self.loadingPage.emit()
    
    def _on_load_finished(self, successful):
        self._load_status = successful
        self.pageLoaded.emit()
        self.load_js()
    
    def play(self, playActions):
        for action in playActions:
            if isinstance(action, actions.UserAction):
                if action.type == 'fill':
                    self.fill(action.selector, action.value)
    
    def load(self, url):
        """Load a web page and return status (a boolean)."""
        self.webframe.load(QUrl(url))
        return self._wait_load()

    def click(self, selector, wait_load=True, timeout=None, assert_exists=True):
        if assert_exists and not self.assertExists(selector):
            raise DomElementNotFound(selector)
        
        jscode = "%s('%s').simulate('click');" % (self.jslib, selector)
        self.runjs(jscode)
        if wait_load:
            return self._wait_load(timeout)
        return True
    
    def clickNearestTo(self, target, near_to, top_parent,  wait_load=True, timeout=None, assert_exists=True):
        if assert_exists and not self.assertExists(near_to):
            raise DomElementNotFound(near_to)
        
        jscode = "%s('%s').closest('%s').find('%s').simulate('click');" % (self.jslib, near_to, top_parent, target)
        self.runjs(jscode)
        if wait_load:
            return self._wait_load(timeout)
        return True
    
    def clickLinkMatching(self, pattern, selector='a', wait_load=True, timeout=None):
        jscode = "%s('%s').filter(function(){ return /%s/i.test(%s(this).text()); }).first().simulate('click');" % (self.jslib, selector, pattern, self.jslib)
        self.runjs(jscode)
        if wait_load:
            return self._wait_load(timeout)
        return True
        
    def runjs(self, jscode, debug=True):
        res = self.webframe.evaluateJavaScript(jscode)
        self.webframe.evaluateJavaScript('$();')
        return res    
        
    def _wait_load(self, timeout=None):
        app = QApplication.instance()
        app.processEvents()
        if self._load_status is not None:
            load_status = self._load_status
            self._load_status = None
            return load_status
        itime = time.time()
        while self._load_status is None:
            if timeout and time.time() - itime > timeout:
                raise SpynnerTimeout("Timeout reached: %d seconds" % timeout)
            app.processEvents()
        app.processEvents()    
        #if self._load_status:
            #self.load_js()
            #self.webpage.setViewportSize(self.webpage.mainFrame().contentsSize())
        load_status = self._load_status
        self._load_status = None
        return load_status
    
    def load_jquery(self, force=False):
        """Load jquery in the current frame"""
        jscode = ''
        jscode += self.jquery
        jscode += "\nvar %s = jQuery.noConflict();" % self.jslib
        self.runjs(jscode)

    def load_js(self):
        self.load_jquery()
        self.load_jquery_simulate()
        self.load_jquery_picker()
        self.load_jquery_logger()
        self.webframe.addToJavaScriptWindowObject("_Picker", self.picker)
        self.webframe.addToJavaScriptWindowObject("_Logger", self.logger)
        #self.load_additional_js()
        
    def get_js_obj_length(self, res):
        if res.type() != res.Map:
            return False
        resmap = res.toMap()
        lenfield = QString(u'length')
        if lenfield not in resmap:
            return False
        return resmap[lenfield].toInt()[0]    

    def load_jquery_simulate(self, force=False):
        """Load jquery in the current frame"""
        self.runjs(self.jquery_simulate, debug=False)
        
    def load_jquery_picker(self, force=False):
        """Load jquery picker"""
        self.runjs(self.jquery_picker, debug=False)
        
    def load_jquery_logger(self, force=False):
        """Load jquery logger"""
        self.runjs(self.jquery_logger, debug=False)
        
    def fill(self, selector, value, assert_exists=True, assert_visible=True):
        """Fill an input text with a string value using a jQuery selector."""
        escaped_value = value.replace("'", "\\'")
        if assert_exists and not self.assertExists(selector):
            raise DomElementNotFound(selector)
        
        if assert_visible and not self.assertVisible(selector):
            raise DomElementNotVisible(selector)
            
        jscode = "%s('%s').val('%s');" % (self.jslib, selector, escaped_value)
        self.runjs(jscode)
        
    def select(self, selector, value, assert_exists=True, assert_visible=True):
        escaped_value = value.replace("'", "\\'")
        if assert_exists and not self.assertExists(selector):
            raise DomElementNotFound(selector)
        
        if assert_visible and not self.assertVisible(selector):
            raise DomElementNotVisible(selector)
        
        if not self.assertExists("%s > option[value=%s]" % (selector, value)):
            raise Exception("Could not find an option with value '%s' for select at '%s'" % (value, selector))
            
        jscode = "%s('%s').val('%s');" % (self.jslib, selector, escaped_value)
        self.runjs(jscode)    
        
    def sendText(self, selector, text, keyboard_modifiers = Qt.NoModifier, wait_load=False, wait_requests=None, timeout=None):
        """
        Send text in any element (to fill it for example)

        @param selector: QtWebkit Selector
        @param keys to input in the QT way
        @param wait_load: If True, it will wait until a new page is loaded.
        @param timeout: Seconds to wait for the page to load before
                                       raising an exception.
        @param wait_requests: How many requests to wait before returning. Useful
                              for AJAX requests.

        >>> br.sendKeys('#val_cel_dentifiant', 'fancy text')
        """
        element = self.webframe.findFirstElement(selector)
        element.setFocus()
        eventp = QKeyEvent(QEvent.KeyPress, Qt.Key_A, keyboard_modifiers, QString(text))
        app = QApplication.instance()
        app.sendEvent(self.webview, eventp)
        #self._events_loop(timeout)
        #self.wait_requests(wait_requests)
        if wait_load:
            return self._wait_load(timeout)    
        
    def assertPageTitle(self, regex):
        title = self.webframe.title()
        if not re.search(regex, title, re.I):
            raise Exception("Page title '%s' does not match '%s'" % (title, regex))
        
    def assertInputValue(self, regex, selector):
        jscode = "%s('%s').val()" % (self.jslib, selector)
        result = self.runjs(jscode).toString()
        if not re.search(regex, result, re.I):
            raise Exception("Input value at '%s' does not match '%s', found '%s'" % (selector, regex, result))
        
    def assertTextMatch(self, regex, selector):
        #TODO: avoid rebuild parse tree
        self.parser = pyquery.PyQuery(self.html)
        found_html = self.parser(selector).html();
        if not found_html:
            raise Exception("Could not find DOM element at '%s'" % selector)
        result = re.search(regex, found_html, re.I)
        if not result:
            raise Exception("Could not find text '%s' inside DOM element at '%s'" % (regex, selector))
    
    def assertExists(self, selector):
        jscode = "%s('%s').length" % (self.jslib, selector)
        result = self.runjs(jscode).toBool()
        return result
    
    def assertVisible(self, selector):
        jscode = "%s('%s').is(':visible')" % (self.jslib, selector)
        result = self.runjs(jscode).toBool()
        return result
        
    def _get_html(self):
        return unicode(self.webframe.toHtml())
    
    def _get_current_url(self):
        return self.webframe.url().toString()
    
    def togglePicker(self):
        val = 'false' if self.picker.enabled else 'true'
            
        jscode = "__pickerEnabled = %s;" % val
        self.runjs(jscode, False)
        self.picker.enabled = not self.picker.enabled
    
    # Properties

    html = property(_get_html)
    """Rendered HTML in current page."""
    
    current_url = property(_get_current_url)
    
    
class DomAssertion(Exception):
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self): 
        return self.msg   
    
    
class DomElementNotFound(DomAssertion):
    
    def __init__(self, selector):
        super(DomElementNotFound, self).__init__("Can't find DOM element at '%s'" % selector)
    
class DomElementNotVisible(Exception):
    
    def __init__(self, selector):
        super(DomElementNotVisible, self).__init__("The DOM element at '%s' is not visible by the user" % selector)

class SpynnerError(Exception):
    """General Spynner error."""

class SpynnerPageError(Exception):
    """Error loading page."""

class SpynnerTimeout(Exception):
    """A timeout (usually on page load) has been reached."""
    
class SpynnerJavascriptError(Exception):
    """Error on the injected Javascript code."""