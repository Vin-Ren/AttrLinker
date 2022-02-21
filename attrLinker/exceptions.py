
class AttrLinkerException(RuntimeError):
    '''Base Exception For Whole Package'''
    pass


class LinkerException(AttrLinkerException):
    '''Base Exception for Linker'''
    pass

class ManagerException(AttrLinkerException):
    '''Base Exception for LinkManager'''

class LinkerNotReady(LinkerException):
    '''Linker is not ready'''
    pass

class LinkerExists(ManagerException):
    '''Linker is found in the manager's hashmap of linkers'''
    pass

class LinkerNotFound(ManagerException):
    '''Linker is not found in the manager's hashmap of linkers'''
    pass
