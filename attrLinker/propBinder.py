
class PropBinder:
    '''
    PropBinder behaves similiarly to the whole attrLinker, but, PropBinder makes all instance of the applied/binded class to a specific instance's value.
    
    PropBinder has the advantage of being bindable to other object, without connection to the object going to be binded. 
    Unlike Linker, which can only bind to object that is its attribute.

    PropBinder might be of use to apps which only allow up to 1 instance of a class.
    '''
    def __init__(self, source_obj):
        self.source_obj = source_obj
        self.propList = {}
    
    def __repr__(self):
        return "<{} Source={}>".format(self.__class__.__name__, self.source_obj)
    
    def createProp(self, converter=lambda x:x):
        def _func(_self):
            return converter(self.source_obj)
        return property(_func)
    
    def applyProp(self, prop, target_class, target_name):
        setattr(target_class, target_name, prop)
        self.propList["{}.{}".format(target_class, target_name)] = prop
    
    def bind(self, target_class, target_name, converter=lambda x:x):
        prop = self.createProp(converter)
        return self.applyProp(prop, target_class, target_name)
        
