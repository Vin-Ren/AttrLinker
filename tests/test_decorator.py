from attrLinker.linkMethod import *
from attrLinker.preparedLink import PreparedLink
from attrLinker import LinkedClass
from tests.simple_implementation import User


@LinkedClass
class ImplementedUser(User):
    __LINKS__ = [PreparedLink(MultiDictionary, 'userData', linkMap=['id', 'name', 'online_time', 'status', 'sent_messages'], enableSetter=True),
                 PreparedLink(MultiList, 'sent_messages', linkMap={'first_message': 0, 'last_message': -1}, enableSetter=True),
                 PreparedLink(FormattedText, 'userData', 'name_tag', formattable_text='{name}#{id}'),
                 PreparedLink(Object, 'online_time', 'login_time')
                 ]

# Initialize object
user = ImplementedUser(id=1234, name='Steve')
user.send_message('Hi There!')
user.send_message('Goodbye!')


def test_multiLinkDictionary():
    for linked in ImplementedUser.__LINKS__[0].executionKwargs['linkMap']:
        assert user.__getattribute__(linked) == user.userData.get(linked), "{0} does not match. ({1}!={2})".format(linked, user.__getattribute__(linked), user.userData.get(linked))

def test_multiLinkList():
    for linkedAttr, linkedIdx in ImplementedUser.__LINKS__[1].executionKwargs['linkMap'].items():
        assert user.__getattribute__(linkedAttr) == user.sent_messages[linkedIdx], "{0} linked with index {1} does not match. ({2}!={3})".format(linkedAttr, linkedIdx, user.__getattribute__(linkedAttr), user.sent_messages[linkedIdx])

def test_formattedTextFromDict():
    assert user.name_tag == ImplementedUser.__LINKS__[2].executionKwargs['formattable_text'].format(**user.userData), "formattedTextFromDict doesn't behave as expected. __getattribute__={0} text.format={1}".format(user.name_tag, '{name}#{id}'.format(**user.userData))

def test_linkObject():
    assert user.login_time == user.online_time.login_time, "linkObject is not working as expected. user.attr={0} user.obj.attr={1}".format(user.login_time, user.online_time.login_time)
