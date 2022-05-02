from typing import list

from .attrLinker import LinkManager
from .linkMethod import LinkMethod


class PreparedLink:
    def __init__(self, linkMethod: LinkMethod, sourceVar, *args, **kwargs):
        self.linkMethod = linkMethod
        self.sourceVar = sourceVar
        self.executionArgs = args
        self.executionKwargs = kwargs
        
        self._appliedClasses = []
    
    def __repr__(self):
        return "<{} Method={} AppliedCount={}>".format(self.__class__.__name__, LinkMethod(self.linkMethod).name, len(self._appliedClasses))

    def apply(self, targetClass: type):
        if self.linkMethod is None:
            manager = LinkManager._getDefault()
            manager.bind(targetClass, self.sourceVar, *self.executionArgs, **self.executionKwargs)
        else:
            self.linkMethod(targetClass, self.sourceVar, *self.executionArgs, **self.executionKwargs)
        self._appliedClasses.append(targetClass)

    @classmethod
    def applyLinks(targetClass, links:list):
        [link.apply(targetClass) for link in links]
