from .utils import DictUpdater
from .attrLinker import LinkManager

# TODO: Make presets on like, linking to a dictionary's value, list index x, manipulating numbers and strings, etc.
# WARNING: For iterative linking, DO NOT use lambda directly, use it like in multiLinkDictionary using linkDictionary. OR you would be facing an issue, where every targetVar assigned, gets the last link converter.

def linkDictionary(targetClass, sourceVar, targetVar, sourceDictKey, useGet=True, getDefault=None, enableSetter=False, doc='', **kw):
    getterConverter = lambda dict: dict[sourceDictKey]
    setterConverter = lambda linkedSelf, replacement: DictUpdater(linkedSelf.__getattribute__(sourceVar), {sourceDictKey:replacement})
    if useGet:
        getterConverter = lambda dict: dict.get(sourceDictKey, getDefault)
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
