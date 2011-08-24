'''
Created on Aug 23, 2011

@author: fabio
'''

class PickedData(object):

    def __init__(self, selector, elementType, value=None):
        self.selector = selector
        self.elementType = elementType
        self.value = value.trimmed()
        