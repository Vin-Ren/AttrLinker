from enum import Enum

from .presets import linkDictionary, multiLinkDictionary, linkList, multiLinkList, linkObject, multiLinkObject, formattedTextFromDict


class LinkMethod(Enum):
    DirectLink = None # A bypass to manager.bind
    Dictionary = linkDictionary
    MultiDictionary = multiLinkDictionary
    List = linkList
    MultiList = multiLinkList
    Object = linkObject
    MultiObject = multiLinkObject
    FormattedText = formattedTextFromDict

DirectLink = LinkMethod.DirectLink
Dictionary = LinkMethod.Dictionary
MultiDictionary = LinkMethod.MultiDictionary
List = LinkMethod.List
MultiList = LinkMethod.MultiList
Object = LinkMethod.Object
MultiObject = LinkMethod.MultiObject
FormattedText = LinkMethod.FormattedText

__all__ = [
'DirectLink',
'Dictionary',
'MultiDictionary',
'List',
'MultiList',
'Object',
'MultiObject',
'FormattedText'
]