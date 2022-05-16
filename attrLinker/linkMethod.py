from enum import Enum

from .presets import linkDictionary, multiLinkDictionary, linkList, multiLinkList, linkObject, multiLinkObject, formattedTextFromDict


METHODS = {f.__name__:f for f in [linkDictionary, multiLinkDictionary, linkList, multiLinkList, linkObject, multiLinkObject, formattedTextFromDict]}


class LinkMethod(Enum):
    def getMethod(self):
        return METHODS.get(self.value)
    
    def __call__(self, *args, **kwargs):
        meth = self.getMethod()
        return meth(*args, **kwargs)
    
    # Members, being the method name and target function name in string.
    DirectLink = None # A bypass to manager.bind
    Dictionary = 'linkDictionary'
    MultiDictionary = 'multiLinkDictionary'
    List = 'linkList'
    MultiList = 'multiLinkList'
    Object = 'linkObject'
    MultiObject = 'multiLinkObject'
    FormattedText = 'formattedTextFromDict'

DirectLink = LinkMethod.DirectLink
Dictionary = LinkMethod.Dictionary
MultiDictionary = LinkMethod.MultiDictionary
List = LinkMethod.List
MultiList = LinkMethod.MultiList
Object = LinkMethod.Object
MultiObject = LinkMethod.MultiObject
FormattedText = LinkMethod.FormattedText

__all__ = [meth.name for meth in LinkMethod]
