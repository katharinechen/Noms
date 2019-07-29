"""
Produce a valid usertoken from a local user's email address
"""
from __future__ import print_function

from mongoengine import connect

from codado.tx import Main

from noms import user, DB_NAME, DB_CONNECT
from noms.const import ENCODING


class UserToken(Main):
    """
    Print a usertoken for the user represented by the given email
    """
    synopsis = "usertoken <email>"

    def parseArgs(self, email):
        self['email'] = email

    def postOptions(self):
        connect(DB_NAME, DB_CONNECT)
        print(get(self['email']))


def get(email):
    u = user.User.objects.get(email=email)
    return u.asToken().decode(ENCODING)
