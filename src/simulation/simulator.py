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
from logger import *
from picker import *
from exceptions import *
from simulation.actions.assertions import AssertException

class Simulator(QObject):
    
    event_looptime = 0.01
    
    """ Signals emitted by this class """
    loadingPage = pyqtSignal()
    pageLoaded = pyqtSignal()
    pathPicked = pyqtSignal()
    startSimulation = pyqtSignal()
    endSimulation = pyqtSignal()
    startPlayAction = pyqtSignal(int)
    endPlayAction = pyqtSignal(int)
    
    """ Public properties """
    picker = None
    logger = None
    
    """ Protected properties """
    _load_status = None
    
    jQueryAlias = '$' 
    
    """ Protected properties """
    _jquery = 'jquery-1.6.1.js'
    _jquery_simulate = 'jquery.simulate.js'
    

    def __init__(self, model):
        super(Simulator, self).__init__()
        self.actionsModel = model
        self.webpage = QWebPage()
        self.webframe = self.webpage.mainFrame()
        self.networkManager = self.webpage.networkAccessManager()
        
        self.connect(self.networkManager, SIGNAL('finished(QNetworkReply *)'), self._on_network_finished)
        
        self.webpage.connect(self.webpage, SIGNAL('loadFinished(bool)'), self._on_load_finished)
        self.webpage.connect(self.webpage, SIGNAL("loadStarted()"), self._on_load_started)
        
        self.jquery = open(os.path.join(os.path.dirname(__file__), "../javascript/" + self._jquery)).read()
        self.jquery_simulate = open(os.path.join(os.path.dirname(__file__), "../javascript/" + self._jquery_simulate)).read()
        self.jquery_path_builder = open(os.path.join(os.path.dirname(__file__), "../javascript/selector_builder.js")).read()
        self.jquery_picker = open(os.path.join(os.path.dirname(__file__), "../javascript/picker.js")).read()
        self.jquery_logger = open(os.path.join(os.path.dirname(__file__), "../javascript/logger.js")).read()
        self.jquery_selector = open(os.path.join(os.path.dirname(__file__), "../javascript/selector.js")).read()
        
        self.jQueryAlias = '$'
        
        self.picker = Picker();
        self.logger = Logger();
        self.logger.setModel(model)
        
    def _on_network_finished(self, reply):
        request = reply.request()
        ajax_header = request.rawHeader(QByteArray("X-Requested-With"))
        if not ajax_header.isEmpty() and QString(ajax_header).compare("XMLHttpRequest", Qt.CaseInsensitive) == 0:
            self._load_status = True
        
    def createView(self):
        self.webview = QWebView()
        self.webview.setPage(self.webpage)
        
    def getWidget(self):
        return self.webview
        
    def _on_load_started(self):
        self._load_status = None
        self.loadingPage.emit()
    
    def _on_load_finished(self, successful):
        self._load_status = successful
        self.pageLoaded.emit()
        self.load_js()
    
    def play(self, playActions):
        self.startSimulation.emit()
        for index, action in enumerate(playActions):
            modelIndex = self.actionsModel.index(index, 0, QModelIndex())
            self.startPlayAction.emit(index)
            try:
                action.execute(self)
            except AssertException:
                pass
            self.actionsModel.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), modelIndex, modelIndex)
            self.endPlayAction.emit(index)
        self.endSimulation.emit()
                
    def load(self, url):
        """Load a web page and return status (a boolean)."""
        self.webframe.load(QUrl(url))
        return self.wait_load()

    def clickNearestTo(self, target, near_to, top_parent,  wait_load=True, timeout=None, assert_exists=True):
        if assert_exists and not self.assertExists(near_to):
            raise DomElementNotFound(near_to)
        
        jscode = "%s('%s').closest('%s').find('%s').simulate('click');" % (self.jQueryAlias, near_to, top_parent, target)
        self.runjs(jscode)
        if wait_load:
            return self.wait_load(timeout)
        return True
    
    def clickLinkMatching(self, pattern, selector='a', wait_load=True, timeout=None):
        jscode = "%s('%s').filter(function(){ return /%s/i.test(%s(this).text()); }).first().simulate('click');" % (self.jQueryAlias, selector, pattern, self.jQueryAlias)
        self.runjs(jscode)
        if wait_load:
            return self.wait_load(timeout)
        return True
        
    def runjs(self, jscode, debug=True):
        res = self.webframe.evaluateJavaScript(jscode)
        self.webframe.evaluateJavaScript('$();')
        return res    
        
    def wait_load(self, timeout=10):
        app = QApplication.instance()
        app.processEvents()
        if self._load_status is not None:
            load_status = self._load_status
            self._load_status = None
            return load_status
        start_time = time.time()
        
        while self._load_status is None:
            if timeout and time.time() - start_time > timeout:
                raise SimulatorTimeout("Timeout reached: %d seconds" % timeout)
            app.processEvents()
        
        app.processEvents()    
        load_status = self._load_status
        self._load_status = None
        return load_status
    
    def load_jquery(self, force=False):
        """Load jquery in the current frame"""
        jscode = ''
        jscode += self.jquery
        jscode += "\nvar %s = jQuery.noConflict();" % self.jQueryAlias
        self.runjs(jscode)

    def load_js(self):
        self.load_jquery()
        self.load_jquery_simulate()
        self.load_jquery_path_builder()
        self.load_jquery_picker()
        self.load_jquery_logger()
        self.load_jquery_selector()
        self.webframe.addToJavaScriptWindowObject("_Picker", self.picker)
        self.webframe.addToJavaScriptWindowObject("_Logger", self.logger)
        
    def load_jquery_simulate(self, force=False):
        self.runjs(self.jquery_simulate, debug=False)
        
    def load_jquery_picker(self, force=False):
        self.runjs(self.jquery_picker, debug=False)
        
    def load_jquery_path_builder(self, force=False):
        self.runjs(self.jquery_path_builder, debug=False)
        
    def load_jquery_selector(self, force=False):
        self.runjs(self.jquery_selector, debug=False)
        
    def load_jquery_logger(self, force=False):
        self.runjs(self.jquery_logger, debug=False)
        
    def getElementPosition(self, selector):
        jscode = "_off = %s.smartSelector.select('%s').realOffset(); _off.left + ',' + _off.top;" % (self.jQueryAlias, selector)
        res = self.runjs(jscode).toString().split(',')
        x = res[0]
        y = res[1]
        point = QPoint(int(x), int(y))
        rect = self.webframe.geometry()
        where = QPoint(rect.x() + point.x() + 1, rect.y() + point.y() + 1)
        return where
    
    def assertPageTitle(self, regex):
        title = self.webframe.title()
        if not re.search(regex, title, re.I):
            raise Exception("Page title '%s' does not match '%s'" % (title, regex))
        
    def assertInputValue(self, regex, selector):
        jscode = "%s('%s').val()" % (self.jQueryAlias, selector)
        result = self.runjs(jscode).toString()
        if not re.search(regex, result, re.I):
            raise Exception("Input value at '%s' does not match '%s', found '%s'" % (selector, regex, result))
    
    def assertTextMatch(self, regex, selector):
        jscode = "_assert.contentMatch('%s', '%s');" % (regex, selector)
        result = self.runjs(jscode)
        result = result.toBool()
        if not result:
            raise Exception("Could not find text '%s' inside DOM element at '%s'" % (regex, selector))
    
    def assertExists(self, selector):
        #jscode = "%s('%s').length" % (self.jQueryAlias, selector)
        jscode = "%s.smartSelector.select('%s').length > 0" % (self.jQueryAlias, selector)
        result = self.runjs(jscode).toBool()
        return result
    
    def assertVisible(self, selector):
        jscode = "%s('%s').is(':visible')" % (self.jQueryAlias, selector)
        result = self.runjs(jscode).toBool()
        return result
        
    def _get_html(self):
        return unicode(self.webframe.toHtml())
    
    def _get_current_url(self):
        return self.webframe.url().toString()
    
    def togglePicker(self):
        self.picker.toggleEnable()
    
    # Properties

    html = property(_get_html)
    """Rendered HTML in current page."""
    
    current_url = property(_get_current_url)
    
class SimulatorTimeout(Exception):
    """A timeout has occurred."""
