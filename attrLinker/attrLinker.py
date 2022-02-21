from .utils import DefaultLambda, DictUpdater
from .exceptions import LinkerExists, LinkerNotFound, LinkerNotReady


class Linker:
    '''Linker object to link between attributes of a class' instance using property'''
    def __init__(self, sourceVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, setterOverrider=None, doc=None):
        '''
        Params
        ------
        sourceVar:str is the source instance variable name
        getterConverter:Callable is the function that gets called to process the sourceVar's value. Called with a single argument, which is the instance self.
        setterConverter:Callable is the function that gets called to process a replacement before being set to the sourceVar. Called with 2 args=(instance_self, replacement)
        setterOverrider:Callable is the function that gets called to do the setter process. Called with 3 args=(instance_self, Linker.sourceVar, replacement)
        doc:str is the documentation string (docstring) for the property
        '''
        self.sourceVar = sourceVar
        self.getterConverter = getterConverter
        self.setterOverrider = setterOverrider
        self.setterConverter = setterConverter
        self.doc = doc or "Linker to instance variable: {}".format(self.sourceVar)
        self.property = None
        self.links = {} # dictionary of targetClass and targetVar, Ex: {Class1: [Var1,Var2,Var3,...],...}

    def __repr__(self):
        return "<{} SourceVar={} Ready={}>".format(self.__class__.__name__, self.sourceVar, self.ready)

    def __str__(self):
        return "{} SourceVariable={} ReadyToBeApplied={}".format(self.__class__.__name__, self.sourceVar, self.ready)

    @property
    def ready(self):
        '''Whether the linker has been set up or not.'''
        return isinstance(self.property, property)

    def setup(self, enableSetter=True):
        '''
        Sets up the linker's property. This method needs to be called before applying.
        
        Params
        ------
        enableSetter:bool whether to enable setter for the property or not. Basically a full-access-link(True) or a read-only-link(False). Defaults to True(full access link)
        '''
        # linked self here is an instance of an object, no longer a class
        def _linkGetter(linkedSelf):
            return self.getterConverter(linkedSelf.__getattribute__(self.sourceVar))
        _linkGetter.linker = self

        if self.setterOverrider is None:
            def _linkSetter(linkedSelf,replacement):
                setattr(linkedSelf, self.sourceVar, self.setterConverter(linkedSelf, replacement))
        else:
            def _linkSetter(linkedSelf,replacement):
                self.setterOverrider(linkedSelf, self.sourceVar, replacement) # args=(targetInstanceSelf, linkedVariable, replacement)
        
        _linkSetter.linker = self
        # print(f"{enableSetter=}") # DEBUG
        self.property = property(fget=_linkGetter, fset=_linkSetter if enableSetter else None, doc=self.doc)
        return self # Support calling chain. Ex: Linker(...).setup().apply(...)

    def apply(self, targetClass, targetVar):
        '''
        Applies the linker to given class at the target variable name.

        Params
        ------
        targetClass:type is the class targeted to be linked with
        targetVar:str is the class's instance attribute name to be linked at
        '''
        if not self.ready:
            raise LinkerNotReady("Linker is not ready yet! Please call setup first to set it up.")
        setattr(targetClass, targetVar, self.property)
        self.links[targetClass] = self.links.get(targetClass, []) + [targetVar] #Ex: {Class1: [Var1,Var2,...]}


class LinkManager:
    _DEFAULT_MANAGER = None # Manager for preset linkers/bindings
    _MANAGERS = [] # Keep track of created managers
    _LINKER_CLASS = Linker # Linker class to create links

    def __new__(cls):
        # Keep track of managers
        instance = super().__new__(cls)
        cls._MANAGERS.append(instance)
        return instance

    @classmethod
    def _getDefault(cls):
        '''Gets the default link manager, if not available, create one. Used by presets.'''
        if not isinstance(cls._DEFAULT_MANAGER, cls):
            cls._DEFAULT_MANAGER = cls()
        return cls._DEFAULT_MANAGER

    @classmethod
    def changeLinkerClass(cls, linkerClass):
        '''
        Change Linker Class if needed, or for experimental purposes. Given Linker Class replacement MUST inherit from the original Linker Class.

        Params
        ------
        linkerClass:type is the replacement for LinkManager's linker class.
        '''
        if not issubclass(linkerClass, Linker):
            raise RuntimeError('Given Linker Class Replacement Must Inherit From <Linker>.')
        cls._LINKER_CLASS = linkerClass

    def __init__(self, autoLinkWithManager=True, linkerSetupOptions={}):
        '''
        Params
        ------
        autoLinkWithManager:bool is whether to record the link pairs in the LinkManager's links attribute
        linkerSetupOpntions:dict is to update the default setup options of the LinkManager'''
        self.autoLinkWithManager = autoLinkWithManager
        self.linkerSetupOptions = DictUpdater({'enableSetter':True}, linkerSetupOptions)
        self.linkers = {}
        self.links = {}

    def __repr__(self):
        return "<{} LinkerClass={} LinkersCount={}>".format(self.__class__.__name__, self.linkerClass, len(self.linkers))

    @property
    def linkerClass(self):
        return self.__class__._LINKER_CLASS

    def createLinker(self, name, sourceVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, setterOverrider=None, doc='', overwrite=False, doSetup=True, setupOptions={}):
        '''
        Creates a linker object with given arguments, and put it into a hashmap on the LinkManager linkers attribute, then call its setup method if doSetup is True.

        Params
        ------
        name:str the name to be paired with the linker in the Manager's hashmap
        sourceVar:str the source attribute name of an instance for the linker to later be applied to
        getterConverter:Callable is the function that gets called to process the sourceVar's value
        setterConverter:Callable is the function that gets called to process a replacement before being set to the sourceVar
        setterOverrider:Callable is the function that gets called to do the setter process
        doc:str is the documentation string (docstring) for the property
        overwrite:bool whether to overwrite existing entries if found with the same name on the hashmap
        doSetup:bool whether to call the setup method of the linker after its creation
        setupOptions:dict extra setup options for the linker.setup method in the form of a dictionary
        '''
        if not overwrite and self.linkers.get(name) is not None:
            raise LinkerExists("A Linker with name '{}' already exists in this linker manager. To overwrite it, please set overwrite=True.".format(name))
        self.linkers[name] = self.linkerClass(sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, setterOverrider=setterOverrider, doc=doc)
        if doSetup:
            setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
            self.linkers[name].setup(**setupOptions)
        return self.linkers[name] # if they wanted to use it through call chaining, they can. Ex: AttrLinkManager().createLinker(...).apply(...)

    def prepareLinkers(self, setupOptions={}):
        '''
        Calls the setup method for every linker in the manager's hashmap.
        
        Params
        ------
        setupOptions:dict extra setup options for the linker.setup method in the form of a dictionary
        '''
        # Setup linkers
        setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
        [linker.setup(**setupOptions) for linker in self.linkers]

    def applyLinker(self, linkerName, targetClass, targetVar):
        '''
        Applies the linker with given linkerName to given class at the target variable name.

        Params
        ------
        linkerName:str is the name of the linker in the manager's hashmap
        targetClass:type is the class targeted to be linked with
        targetVar:str is the class's instance attribute name to be linked at
        '''
        try:
            self.linkers[linkerName].apply(targetClass, targetVar)
            if self.autoLinkWithManager:
                self.links[targetClass] = (targetVar, self.linkers[linkerName])
        except KeyError as exc:
            raise LinkerNotFound('Linker {} is not found in the manager. Make sure you enter the correct name, or create one if it does not exists.'.format(linkerName)) from exc

    def bind(self, targetClass, sourceVar, targetVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, setterOverrider=None, doc='', setupOptions={}, name=None, orphan=False, **kw):
        '''
        Creates linker and apply it to the targetClass, then store it with generated name or given name, or orphan it.

        Params
        ------
        targetClass:type is the class targeted to be linked with
        sourceVar:str the source attribute name of an instance for the linker to later be applied to
        targetVar:str is the class's instance attribute name to be linked at
        getterConverter:Callable is the function that gets called to process the sourceVar's value
        setterConverter:Callable is the function that gets called to process a replacement before being set to the sourceVar
        setterOverrider:Callable is the function that gets called to do the setter process
        doc:str is the documentation string (docstring) for the property
        setupOptions:dict extra setup options for the linker.setup method in the form of a dictionary
        name:str the name to be paired with the linker in the Manager's hashmap
        orphan:bool whether to orphan the linker after linking. Meaning leaving no bindings between the linker and manager. Defaults to False.

        Extra keyword argument passed, would be passed directly to manager.createLinker (Only if orphan is disabled)
        '''
        # generates name for the linker, or just make one and orphan/delete it after binding.
        setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
        # print(setupOptions) # DEBUG
        if orphan:
            linker = self.linkerClass(sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, setterOverrider=setterOverrider, doc=doc)
            linker.setup(**setupOptions)
            linker.apply(targetClass, targetVar)
            # del linker
            return linker
        
        # Generate a name if not given, though not nice looking, it should not be possible for any duplicates under normal usage, 
        # where each targetVar for each class is used once only.
        name = str(name or '{}-class:{};source:{};target:{}'.format(self.linkerClass, targetClass, sourceVar, targetVar))
        self.createLinker(name, sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, setterOverrider=setterOverrider, doc=doc, setupOptions=setupOptions, **kw)
        self.applyLinker(name, targetClass, targetVar)

