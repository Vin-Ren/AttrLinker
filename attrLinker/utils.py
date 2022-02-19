
# Useful Consts
DefaultLambda = lambda x:x
DictUpdater = lambda dbase,dupdater: (lambda base,updater:[base.update(updater), base][-1])(dbase.copy(), dupdater)
