"""
Test the User object
"""
from twisted.trial import unittest

from noms import user
from noms.test import mockDatabase


class UserTest(unittest.TestCase):
    """
    Cover the User object and related
    """
    def test_fromSSO(self):
        """
        Do I create a valid user object from SSO registration?
        """
        ssoData = {
                'email': 'ssodude@ssoplace.com',
                'given_name': 'Sso',
                'family_name': 'Dude',
                }
        with mockDatabase():
            u = user.User.fromSSO(ssoData)
            x = user.User.objects(email='ssodude@ssoplace.com').first()
            self.assertEqual(x.id, u.id)
            self.assertEqual(x.familyName, ssoData['family_name'])
            self.assertEqual(x.roles, [user.Roles.user])

    def test_safe(self):
        """
        Do I produce a web-safe rendering of the user object?
        """
        u = user.User(email='hello@hello.com', roles=[user.Roles.user])
        self.assertEqual(u.safe(),
               {'email': u'hello@hello.com',
                'givenName': None,
                'familyName': None,
                'roles': [u'user'],
                })
