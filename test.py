from attrLinker.presets import multiLinkDictionary


class User:
    def __init__(self):
        self.userData = {}

    def fetchData(self):
        self.userData = {'id':1, 'Name':'Foo', 'online_time':0, 'status': 'idle'}
        
# linkMap pair => {source_key: destination_attribute, ...}
linkMap = {'id':'ID', 'online_time':'onlineTime', 'status':'status', 'Name':'name'}
multiLinkDictionary(User, sourceVar='userData', linkMap=linkMap, enableSetter=True)
# IMPORTANT: please do not link inside __init__. 

testuser = User()
testuser.fetchData()

def testDictMap(obj, attrsMap):
    for key, attr in attrsMap.items():
        try:
            assert testuser.__getattribute__(attr) == testuser.userData.get(key)
            print("Attribute={} Matches Key={}. Value={}".format(attr, key, testuser.__getattribute__(attr)))
        except AssertionError as exc:
            raise AssertionError('Attribute={} and Key={} Does not match.'.format(attr, key))

testDictMap(testuser, linkMap)
