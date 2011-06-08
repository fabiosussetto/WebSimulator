'''
Created on May 31, 2011

@author: fabio
'''

import os
import time

from PyQt4.QtCore import SIGNAL, QUrl, QString, Qt, QEvent
from PyQt4.QtCore import QSize, QDateTime, QPoint
from PyQt4.QtGui import QApplication, QImage, QPainter
from PyQt4.QtGui import QCursor, QMouseEvent, QKeyEvent
from PyQt4.QtNetwork import QNetworkCookie, QNetworkAccessManager
from PyQt4.QtNetwork import QNetworkCookieJar, QNetworkRequest, QNetworkProxy
from PyQt4.QtWebKit import QWebPage, QWebView


class Simulator(object):
    '''
    classdocs
    '''
    _jquery = 'jquery-1.6.1.js'
    _jquery_simulate = 'jquery.simulate.js'

    def __init__(self):
        '''
        Constructor
        '''
        #self.application = application
        self.webpage = QWebPage()
        #self.webpage.userAgentForUrl = 'test'
        self.webframe = self.webpage.mainFrame()
        
        self.webpage.connect(self.webpage, SIGNAL('loadFinished(bool)'), self._on_load_finished)
        self.webpage.connect(self.webpage, SIGNAL("loadStarted()"), self._on_load_started)
        
        self.jquery = open(os.path.join(os.path.dirname(__file__), "../javascript/" + self._jquery)).read()
        self.jquery_simulate = open(os.path.join(os.path.dirname(__file__), "../javascript/" + self._jquery_simulate)).read()
        
        self.jslib = '$'
        self._load_status = None
        
    def createView(self):
        self.webview = QWebView()
        self.webview.setPage(self.webpage)
        
    def getWidget(self):
        return self.webview
        
    def _on_load_started(self):
        self._load_status = None
    
    def _on_load_finished(self, successful):
        self._load_status = successful
        self.load_js()
    
    
    def load(self, url):
        """Load a web page and return status (a boolean)."""
        self.webframe.load(QUrl(url))
        return self._wait_load()

    def click(self, selector, wait_load=False, wait_requests=None, timeout=None):
        jscode = "%s('%s').simulate('click');" % (self.jslib, selector)
        self.runjs(jscode)
        return self._wait_load(timeout)
        #self.wait_requests(wait_requests)
        
    def runjs(self, jscode, debug=True):
        res = self.webframe.evaluateJavaScript(jscode)
        return res    
        
    def _wait_load(self, timeout=None):
        #return
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
        
    def fill(self, selector, value):
        """Fill an input text with a string value using a jQuery selector."""
        escaped_value = value.replace("'", "\\'")
        jscode = "%s('%s').val('%s');" % (self.jslib, selector, escaped_value)
        self.runjs(jscode)
        self.runjs('$();')

class SpynnerError(Exception):
    """General Spynner error."""

class SpynnerPageError(Exception):
    """Error loading page."""

class SpynnerTimeout(Exception):
    """A timeout (usually on page load) has been reached."""
    
class SpynnerJavascriptError(Exception):
    """Error on the injected Javascript code."""