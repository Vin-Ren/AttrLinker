from .utils import DefaultLambda, DictUpdater
from .exceptions import LinkerExists, LinkerNotFound, LinkerNotReady


class Linker:
    '''Linker object to link between attributes with property'''
    def __init__(self, sourceVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, doc=None):
        self.sourceVar = sourceVar
        self.getterConverter = getterConverter
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
        return isinstance(self.property, property)

    def setup(self, enableSetter=True):
        # linked self here is an instance of an object, no longer a class
        def _linkGetter(linkedSelf):
            return self.getterConverter(linkedSelf.__getattribute__(self.sourceVar))
        def _linkSetter(linkedSelf,replacement):
            setattr(linkedSelf, self.sourceVar, self.setterConverter(linkedSelf, replacement))
        _linkGetter.linker = self
        _linkSetter.linker = self
        # print(f"{enableSetter=}") # DEBUG
        self.property = property(fget=_linkGetter, fset=_linkSetter if enableSetter else None, doc=self.doc)
        return self # Support calling chain. Ex: Linker(...).setup().apply(...)

    def apply(self, targetClass, targetVar):
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
        ''
        if not isinstance(cls._DEFAULT_MANAGER, cls):
            cls._DEFAULT_MANAGER = cls()
        return cls._DEFAULT_MANAGER

    @classmethod
    def changeLinkerClass(cls, linkerClass):
        '''Change Linker Class if needed, or for experimental purposes. Given Linker Class replacement MUST inherit from the original Linker Class.'''
        if not issubclass(linkerClass, Linker):
            raise RuntimeError('Given Linker Class Replacement Must Inherit From <Linker>.')
        cls._LINKER_CLASS = linkerClass

    def __init__(self, autoLinkWithManager=True, linkerSetupOptions={}):
        self.autoLinkWithManager = autoLinkWithManager
        self.linkerSetupOptions = DictUpdater({'enableSetter':True}, linkerSetupOptions)
        self.linkers = {}
        self.links = {}

    def __repr__(self):
        return "<{} LinkerClass={} LinkersCount={}>".format(self.__class__.__name__, self.linkerClass, len(self.linkers))

    @property
    def linkerClass(self):
        return self.__class__._LINKER_CLASS

    def createLinker(self, name, sourceVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, doc='', overwrite=False, doSetup=True, setupOptions={}):
        if not overwrite and self.linkers.get(name) is not None:
            raise LinkerExists("A Linker with name '{}' already exists in this linker manager. To overwrite it, please set overwrite=True.".format(name))
        self.linkers[name] = self.linkerClass(sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, doc=doc)
        if doSetup:
            setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
            self.linkers[name].setup(**setupOptions)
        return self.linkers[name] # if they wanted to use it through call chaining, they can. Ex: AttrLinkManager().createLinker(...).apply(...)

    def prepareLinkers(self, setupOptions={}):
        # Setup linkers
        setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
        [linker.setup(**setupOptions) for linker in self.linkers]

    def applyLinker(self, linkerName, targetClass, targetVar):
        try:
            self.linkers[linkerName].apply(targetClass, targetVar)
            if self.autoLinkWithManager:
                self.links[targetClass] = (targetVar, self.linkers[linkerName])
        except KeyError as exc:
            raise LinkerNotFound('Linker {} is not found in the manager. Make sure you enter the correct name, or create one if it does not exists.'.format(linkerName)) from exc

    def bind(self, targetClass, sourceVar, targetVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, doc='', setupOptions={}, name=None, orphan=False, **kw):
        # generates name for the linker, or just make one and orphan/delete it after binding.
        setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
        # print(setupOptions) # DEBUG
        if orphan:
            linker = self.linkerClass(sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, doc=doc)
            linker.setup(**setupOptions)
            linker.apply(targetClass, targetVar)
            # del linker
            return linker
        
        # Generate a name if not given, though not nice looking, it should not be possible for any duplicates under normal usage, 
        # where each targetVar for each class is used once only.
        name = str(name or '{}-class:{};source:{};target:{}'.format(self.linkerClass, targetClass, sourceVar, targetVar))
        self.createLinker(name, sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, doc=doc, setupOptions=setupOptions, **kw)
        self.applyLinker(name, targetClass, targetVar)

