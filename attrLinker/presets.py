from .utils import DictUpdater
from .attrLinker import LinkManager

# TODO: Make presets on like, linking to a dictionary's value, list index x, manipulating numbers and strings, etc.
# WARNING: For iterative linking, DO NOT use lambda directly, use it like in multiLinkDictionary using linkDictionary. OR you would be facing an issue, where every targetVar assigned, gets the last link converter.

def linkDictionary(targetClass, sourceVar, targetVar, sourceDictKey, default=None, enableSetter=False, doc='', **kw):
    '''
    Link an attribute on an instance of targetClass to the source attribute's key, where the source attribute type is dictionary.
    Example: linkDictionary(Foo, 'dictionary', 'bar', 'bar_key', default='default_value')
    'Foo.bar' Gets value by 'Foo.dictionary.get('bar_key', 'default_value')'

    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass, which must be of type dict
    targetVar:str is the attribute name on the class to be linked to
    sourceDictKey:str is the key to access the source dictionary
    default:Any is the default return value for dictionary.get
    enableSetter:bool is basically, whether you want the targetVar attribute to have read-only access or full-access to the variable. Defaults to False(read-only)
    doc:str is the documentation string for the property created
    
    Extra keyword argument passed, would be passed directly to manager.bind
    '''
    getterConverter = lambda dict: dict.get(sourceDictKey, default)
    setterConverter = lambda linkedSelf, replacement: DictUpdater(linkedSelf.__getattribute__(sourceVar), {sourceDictKey:replacement})
    manager = LinkManager._getDefault()
    manager.bind(targetClass, sourceVar, targetVar, getterConverter, setterConverter, setupOptions={'enableSetter': enableSetter}, doc=doc, **kw)


def multiLinkDictionary(targetClass, sourceVar, linkMap={}, **kw):
    '''
    Calls linkDictionary for every pair in linkMap.

    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass, which must be of type dict
    linkMap:dict is the mapping for the linking, the mapping should be in the format as follows: {attribute_name_on_instance:key_in_dictionary,...}

    Extra keyword argument passed, would be passed directly to linkDictionary
    '''
    for targetVar, sourceDictKey in linkMap.items():
        linkDictionary(targetClass, sourceVar, targetVar, sourceDictKey, **kw)


def formattedTextFromDict(targetClass, sourceVar, targetVar, formattable_text, **kw):
    '''
    Creates a formatted text from given formattable_text which is formatted with the sourceVar dictionary.
    Similiar to linkDictionary, except you specify the dictionary keys in the formattable_text, and you could specify multiple keys. Also setter is not available here.
    Would incurr a KeyError if the key(s) in the formattable_text is not found in given source dictionary.
    Example: formattedTextFromDict(User, 'data', 'full_name', '{first_name} {last_name}')
    'User.full_name' value is '{first_name} {second_name}'.format(**User.data)
    
    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass, which must be of type dict
    targetVar:str is the attribute name on the class to be linked to
    formattable_text:str is the text to be formatted with the data from the source. the format of the formattable_text is "{key} {key2}" and so on.
    
    Extra keyword argument passed, would be passed directly to manager.bind
    '''
    getterConverter = lambda dict: formattable_text.format(**dict)
    manager = LinkManager._getDefault()
    manager.bind(targetClass, sourceVar, targetVar, getterConverter, setupOptions={'enableSetter':False}, **kw)


def linkList(targetClass, sourceVar, targetVar, sourceIndex, enableSetter=False, doc='', **kw):
    '''
    Link an attribute on an instance of targetClass to source attribute's item on given index. 
    Example: linkList(Foo, '_list_of_bars', 'first_bar', 0)
    'Foo.first_bar' Gets its value by 'Foo._list_of_bars[0]'

    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass
    targetVar:str is the attribute name on the class to be linked to
    sourceIndex:int is the target index on the source object
    enableSetter:bool is basically, whether you want the targetVar attribute to have read-only access or full-access to the variable. Defaults to False(read-only)
    doc:str is the documentation string for the property created
    
    Extra keyword argument passed, would be passed directly to manager.bind
    '''
    getterConverter = lambda _lst: _lst[sourceIndex]
    setterOverrider = lambda linkedSelf, linkedVar, replacement: [linkedSelf.__getattribute__(linkedVar).pop(sourceIndex), linkedSelf.__getattribute__(linkedVar).insert(sourceIndex, replacement)]
    manager = LinkManager._getDefault()
    manager.bind(targetClass, sourceVar, targetVar, getterConverter, setterOverrider=setterOverrider, setupOptions={'enableSetter': enableSetter}, doc=doc, **kw)


def multiLinkList(targetClass, sourceVar, linkMap={}, **kw):
    '''
    Calls linkList for every pair in linkMap.

    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass, which must be of type list
    linkMap:dict is the mapping for the linking, the mapping should be in the format as follows: {attribute_name_on_instance:index_in_list,...}

    Extra keyword argument passed, would be passed directly to linkList
    '''
    for targetVar, sourceListIndex in linkMap.items():
        linkList(targetClass, sourceVar, targetVar, sourceListIndex, **kw)


def linkObject(targetClass, sourceVar, targetVar, sourceAttribute, enableSetter=False, doc='', **kw):
    '''
    Link an attribute on an instance of targetClass to source attribute's attribute, where the source attribute type is Any.
    Example: linkObject(Foo, 'obj', 'obj_attr1', 'attr_1')
    'Foo.obj_attr1' Gets value by 'Foo.obj.attr_1'

    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass
    targetVar:str is the attribute name on the class to be linked to
    sourceAttribute:str is the attribute name on the source object
    enableSetter:bool is basically, whether you want the targetVar attribute to have read-only access or full-access to the variable. Defaults to False(read-only)
    doc:str is the documentation string for the property created
    
    Extra keyword argument passed, would be passed directly to manager.bind
    '''
    getterConverter = lambda obj: obj.__getattribute__(sourceAttribute)
    #setterConverter = lambda linkedSelf, replacement: (lambda obj: [setattr(obj, sourceAttribute, replacement), obj][-1])(linkedSelf.__getattribute__(sourceVar))
    setterOverrider = lambda linkedSelf, linkedVar, replacement: setattr(linkedSelf.__getattribute__(linkedVar), sourceAttribute, replacement)
    manager = LinkManager._getDefault()
    manager.bind(targetClass, sourceVar, targetVar, getterConverter, setterOverrider=setterOverrider, setupOptions={'enableSetter': enableSetter}, doc=doc, **kw)


def multiLinkObject(targetClass, sourceVar, linkMap={}, **kw):
    '''
    Calls linkObject for every pair in linkMap.

    Params
    ------
    targetClass:type is the class for the linking to be applied at
    sourceVar:str is the source variable name of an instance of the targetClass
    linkMap:dict is the mapping for the linking, the mapping should be in the format as follows: {attribute_name_on_instance:attribute_on_source_object,...}

    Extra keyword argument passed, would be passed directly to linkList
    '''
    for targetVar, sourceObjectAttr in linkMap.items():
        linkList(targetClass, sourceVar, targetVar, sourceObjectAttr, **kw)
