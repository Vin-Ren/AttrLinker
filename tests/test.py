from attrLinker.presets import multiLinkDictionary, formattedTextFromDict


class User:
    def __init__(self):
        self.userData = {}

    def fetchData(self):
        self.userData = {'id':1, 'Name':'Foo', 'online_time':0, 'status': 'idle'}
        
# linkMap pair => {destination_attribute: source_key, ...}
linkMap = {'ID':'id', 'name':'Name', 'onlineTime':'online_time', 'status':'status'}
multiLinkDictionary(User, sourceVar='userData', linkMap=linkMap, enableSetter=True)
formattedTextFromDict(User, 'userData', 'nameTag', "{Name}#{id}")
# IMPORTANT: please do not link inside __init__. 

testuser = User()
testuser.fetchData()

def testDictMap(user, attrsMap):
    for attr, key in attrsMap.items():
        try:
            assert user.__getattribute__(attr) == user.userData.get(key)
            print("Attribute={} Matches Key={}. Value={}".format(attr, key, user.__getattribute__(attr)))
        except AssertionError as exc:
            raise AssertionError('Attribute={} and Key={} Does not match. Exc={}'.format(attr, key, '{e}{e.args}'.format(e=exc)))

testDictMap(testuser, linkMap)
assert testuser.nameTag == "{Name}#{id}".format(**testuser.userData)
