'''
Created on Jun 18, 2011

@author: fabio
'''
import inspect
import re

class TestCase(object):

    def __init__(self, simulator):
        self.simulator = simulator
    
    def run(self):
        #print inspect.getmembers(self, lambda method: re.match("test", method))
        test_methods = inspect.getmembers(self, self._isTestMethod)
        test_methods.sort(key=self.linenumber_of_member)
        getattr(self, 'startCase')()
        for method in test_methods:
            print "Executing test case %s ..." % method[0]
            getattr(self, 'setUp')()
            getattr(self, method[0])()
            getattr(self, 'tearDown')()
            print "... completed"
        getattr(self, 'endCase')()
            
    def startCase(self):
        return True

    def endCase(self):
        return True
    
    def setUp(self):
        return True
        
    def tearDown(self):
        return True
    
        
    def _isTestMethod(self, method):
        return inspect.ismethod(method) and re.match("test", method.__name__)
    
    def linenumber_of_member(self, m):
        try:
            return m[1].im_func.func_code.co_firstlineno
        except AttributeError:
            return -1
    
    
        