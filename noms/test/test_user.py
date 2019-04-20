"""
Test the User object
"""
from noms import user
from noms.test.conftest import requestJSON


def test_fromSSO(mockDatabase):
    """
    Do I create a valid user object from SSO registration?
    """
    ssoData = {
            'email': 'ssodude@ssoplace.com',
            'given_name': 'Sso',
            'family_name': 'Dude',
            }
    u = user.User.fromSSO(ssoData)
    x = user.User.objects(email='ssodude@ssoplace.com').first()
    assert x.id == u.id
    assert x.familyName == ssoData['family_name']
    assert x.roles == [user.Roles.user]


def test_safe():
    """
    Do I produce a web-safe rendering of the user object?
    """
    u = user.User(email='hello@hello.com', roles=[user.Roles.user])

    assert u.safe() == {
            'email': u'hello@hello.com',
            'givenName': None,
            'familyName': None,
            'roles': [u'user'],
            }


def test_anonymousAlreadyExists():
    """
    Do we return the already-existing anonymous user if it already exists?
    """
    anon = user.USER().anonymous
    new1 = user.USER().anonymous
    assert anon.id == new1.id


def test_fromToken(mockDatabase, localapi):
    """
    Can I construct an auth token from user that returns that same user?
    """
    rq = requestJSON([], user=localapi)
    u = user.User.fromRequest(rq)
    assert u.id == localapi.id

    # Create a deliberately incorrect token and see if it fails to auth
    # (failure == anonymous user)
    rq2 = requestJSON([], requestHeaders=[('x-token', [b'asdfasdf'])])
    u2 = user.User.fromRequest(rq2)
    assert u2 is user.USER().anonymous
