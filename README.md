# AttrLinker
Attribute Linker for class instances.

# Examples
For dynamically updated data with many keys
```py
from attrLinker.presets import multiLinkDictionary


class User:
    def __init__(self):
        self.userData = {}

    def fetchData(self):
        self.userData = {'id':1, 'Name':'Foo', 'online_time':0, 'status': 'idle'}
        
# linkMap pair => {source_key: destination_attribute, ...}
linkMap = {'id':'ID', 'online_time':'onlineTime', 'status':'status'}
multiLinkDictionary(User, sourceVar='userData', linkHashMap=linkMap)
# IMPORTANT: please do not link inside __init__. 

>>> testuser = User()
>>> testuser.fetchData()
>>> testuser.ID
1
>>> testuser.onlineTime
0
>>> testuser.status
'idle'
>>> testuser.userData
{'id': 1, 'Name': 'Foo', 'online_time': 0, 'status': 'idle'}
>>> testuser.onlineTime+=10
>>> testuser.userData
{'id': 1, 'Name': 'Foo', 'online_time': 10, 'status': 'idle'}

```