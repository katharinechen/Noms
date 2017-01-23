"""
Produce a valid usertoken from a local user's email address
"""
from mongoengine import connect

from codado.tx import Main

from noms import user, DBHost


class Options(Main):
    synopsis = "usertoken <email>"
    optParameters = [
            ['alias', None, 'noms', 'Alias for a database connection (see noms.DBAlias)'],
            ]

    def parseArgs(self, email):
        self['email'] = email

    def postOptions(self):
        print get(self['email'], alias=self['alias'])


def get(email, alias):
    connect(**DBHost[alias])
    u = user.User.objects.get(email=email)
    return u.asToken()
