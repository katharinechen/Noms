"""
Produce a valid usertoken from a local user's email address
"""
from mongoengine import connect

from codado.tx import Main

from noms import user, DBHost, DBAlias


class UserToken(Main):
    """
    Print a usertoken for the user represented by the given email
    """
    synopsis = "usertoken <email>"

    def parseArgs(self, email):
        self['email'] = email

    def postOptions(self):
        alias = self.parent['alias']
        assert alias in DBAlias
        connect(**DBHost[alias])
        print get(self['email'])


def get(email):
    u = user.User.objects.get(email=email)
    return u.asToken()
