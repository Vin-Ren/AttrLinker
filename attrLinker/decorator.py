
def LinkedClass(cls):
    if cls.__LINKS__ is None:
        return cls
    for link in cls.__LINKS__:
        link.apply(cls)
    return cls
