"""
Test the User object
"""
from noms import user


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
    anon = user.ANONYMOUS()
    new1 = user.ANONYMOUS()
    assert anon.id == new1.id
