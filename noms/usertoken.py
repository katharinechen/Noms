"""
Produce a valid usertoken from a local user's email address
"""
from mongoengine import connect

from twisted.python import usage

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
        connect(**DBHost[self['alias']])
        u = user.User.objects.get(email=self['email'])
        print u.asToken()
