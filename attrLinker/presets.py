from .utils import DictUpdater
from .attrLinker import LinkManager

# TODO: Make presets on like, linking to a dictionary's value, list index x, manipulating numbers and strings, etc.
# WARNING: For iterative linking, DO NOT use lambda directly, use it like in multiLinkDictionary using linkDictionary. OR you would be facing an issue, where every targetVar assigned, gets the last link converter.

def linkDictionary(targetClass, sourceVar, targetVar, sourceDictKey, default=None, enableSetter=False, doc='', **kw):
    '''
    Link an attribute on an object to another attribute's key, where the other attribute type is dictionary.
    Example: linkDictionary(Foo, 'dictionary', 'bar', 'bar_key', default='default_value')
    Foo.bar > Gets value from > Foo.dictionary.get('bar_key', 'default_value')
    '''
    getterConverter = lambda dict: dict.get(sourceDictKey, default)
    setterConverter = lambda linkedSelf, replacement: DictUpdater(linkedSelf.__getattribute__(sourceVar), {sourceDictKey:replacement})
    manager = LinkManager._getDefault()
    manager.bind(targetClass, sourceVar, targetVar, getterConverter, setterConverter, setupOptions={'enableSetter': enableSetter}, doc=doc, **kw)


def multiLinkDictionary(targetClass, sourceVar, linkMap={}, **kw):
    for sourceDictKey, targetVar in linkMap.items():
        linkDictionary(targetClass, sourceVar, targetVar, sourceDictKey, **kw)
       

def linkObject(targetClass, sourceVar, targetVar, sourceAttribute, enableSetter=False, doc='', **kw):
    getterConverter = lambda obj: obj.__getattribute__(sourceAttribute)
    setterConverter = lambda linkedSelf, replacement: (lambda obj: [setattr(obj, sourceAttribute, replacement), obj][-1])(linkedSelf.__getattribute__(sourceVar))
    manager = LinkManager._getDefault()
    manager.bind(targetClass, sourceVar, targetVar, getterConverter, setterConverter, setupOptions={'enableSetter': enableSetter}, doc=doc, **kw)
