
class AttrLinkManager:
    _DEFAULT_MANAGER = None # Manager for preset linkers/bindings
    _MANAGERS = [] # Keep track of created managers
    _LINKER_CLASS = Linker
    # TODO: Make presets on like, linking to a dictionary's value, list index x, manipulating numbers and strings, etc.

    def __new__(cls):
        instance = super().__new__(cls)
        cls._MANAGERS.append(instance)
        return instance

    @classmethod
    def _getDefault(cls):
        if not isinstance(cls._DEFAULT_MANAGER, cls):
            cls._DEFAULT_MANAGER = cls()
        return cls._DEFAULT_MANAGER

    @classmethod
    def changeLinkerClass(cls, linkerClass):
        if not issubclass(linkerClass, Linker):
            raise RuntimeError('Given Linker Class Replacement Must Inherit From <Linker>.')
        cls._LINKER_CLASS = linkerClass

    def __init__(self, autoLinkWithManager=True, linkerSetupOptions={}):
        self.autoLinkWithManager = autoLinkWithManager
        self.linkerSetupOptions = DictUpdater({'enableSetter':True}, linkerSetupOptions)
        self.linkers = {}
        self.links = {}

    def __repr__(self):
        return "<{} SourceVar={} LinkerClass={} LinkersCount={}>".format(self.__class__.__name__, self.sourceVar, self.linkerClass, len(self.linkers))

    @property
    def linkerClass(self):
        return self.__class__._LINKER_CLASS

    def createLinker(self, name, sourceVar, getterConverter=DefaultLambda, setterConverter=DefaultLambda, doc='', overwrite=False, doSetup=True, setupOptions={}):
        if not self.overwrite and self.linkers.get(name) is not None:
            raise LinkerExists("A Linker with name '{}' already exists in this linker manager. To overwrite it, please set overwrite=True.".format(name))
        self.linkers[name] = self.linkerClass(sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, doc=doc)
        if doSetup:
            setupOptions = DictUpdater(self.linkerSetupOptions, setupOptions)
            self.linkers[name].setup(**self.linkerSetupOptions)
        return self.linkers[name] # if they wanted to use it through call chaining, they can. Ex: AttrLinkManager().createLinker(...).apply(...)

    def prepareLinkers(self, enableSetter=True):
        # Setup linkers
        setupOptions = DictUpdater(self.linkerSetupOptions, {'enableSetter':enableSetter})
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
        if orphan:
            linker = self.linkerClass(sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, doc=doc)
            linker.setup(**setupOptions)
            linker.apply(targetClass, targetVar)
            # del linker
            return linker
        # Not Orphaned
        # Generate a name if not given, though not nice looking, it should not be possible for any duplicates under normal usage, 
        # where each targetVar for each class is used once only.
        name = str(name or '{}-class:{};source:{};target:{}'.format(self.linkerClass, targetClass, sourceVar, targetVar))
        self.createLinker(name, sourceVar, getterConverter=getterConverter, setterConverter=setterConverter, doc=doc, setupOptions=setupOptions, **kw)
        self.applyLinker(name, targetClass, targetVar)

