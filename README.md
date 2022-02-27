# AttrLinker
## What it is
It is what it is, an Attribute Linker for class instances. It links a certain attribute name for the class instances to a certain other attribute name before being returned as a value for given attribute name.

## How does it work?
It works using property. To be more specific, it links an attribute name on the class with property, to its target attribute, which is passed through a converter and then returned as the attribute value.

## What is Presets
To help ease linking stuff, because preparing converters is often tedious.

## What is this for?
IMHO, The best use case for this is in dynamically allocated data, periodically updated data, an example is for an app that periodically fetches data from some server about something, and on it's response, there's a lot of entries, which is needed to be updated on its attributes. You could use property for this, but over a certain point, it will become to repetitive. This is the problem this module strives to solve.

## Examples
### 1. Dynamically Allocated Data
```py
from attrLinker.presets import multiLinkDictionary

class User:
    def __init__(self):
        self.userData = {}

    def fetchData(self):
        if len(self.userData):
            self.userData = {'id':1, 'Name':'Foo', 'online_time':0, 'status': 'idle'}
        else:
            self.userData['status']='online'
            self.userData['online_time']+=1
        
# linkMap pair => {source_key: destination_attribute, ...}
linkMap = {'id':'ID', 'Name':'name', 'online_time':'onlineTime', 'status':'status'}
multiLinkDictionary(User, sourceVar='userData', linkMap=linkMap, enableSetter=True)
# enableSetter set to True to be able to assign value back to it.
# IMPORTANT: please do not link inside __init__. 

>>> testuser = User()
>>> testuser.fetchData()
>>> testuser.ID
1
>>> testuser.name
'Foo'
>>> testuser.onlineTime
0
>>> testuser.status
'idle'
>>> testuser.userData # Checking the data directly
{'id': 1, 'Name': 'Foo', 'online_time': 0, 'status': 'idle'}
>>> testuser.onlineTime+=10 # Change it remotely from the assigned attribute (only if enableSetter is True)
>>> testuser.userData
{'id': 1, 'Name': 'Foo', 'online_time': 10, 'status': 'idle'}
>>> testuser.fetchData() # Simulating new data fetched from a server on the internet
>>> testuser.onlineTime
11
>>> testuser.status
'online'
>>> testuser.userData # Checking the data directly
{'id': 1, 'Name': 'Foo', 'online_time': 11, 'status': 'online'}
```