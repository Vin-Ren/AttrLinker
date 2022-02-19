
class LinkerException(RuntimeError):
    pass

class LinkerNotReady(LinkerException):
    pass

class LinkerExists(LinkerException):
    pass

class LinkerNotFound(LinkerException):
    pass
