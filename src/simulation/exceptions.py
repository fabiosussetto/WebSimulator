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