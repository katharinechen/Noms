"""
Generate an md5 hash for a directory of files
"""
from __future__ import print_function

import hashlib
import os

from humanhash import humanize

from twisted.internet.defer import inlineCallbacks
from twisted.internet import task

import treq

from codado.tx import Main

from noms.whisk import usertoken


LOCALAPI_EMAIL = 'localapi@example.com'


class Digester(Main):
    """
    Print a digest of the given directory; with -U, also send it to the server
    """
    synopsis = "digester <directory>"

    optParameters = [
            ['update-url', 'U', None, 'Append the new hash to the URL and make an HTTP GET to update it'],
            ]

    def parseArgs(self, directory):
        self['directory'] = directory

    def postOptions(self):
        dig = digest(self['directory'])
        self._digest = dig
        print(dig)
        if self['update-url']:
            return task.react(self.doUpdate)

    @inlineCallbacks
    def doUpdate(self, reactor):
        """
        Make an HTTP GET to update-url with the new digest
        """
        url = self['update-url'] + self._digest
        token = usertoken.get(LOCALAPI_EMAIL)
        res = yield treq.get(url, headers={'x-token': token})
        response = yield res.content()

        assert res.code == 200, 'Fail %s\n%s' % (res.code, response)

        print('update success')


def digest(path):
    """
    Produce a human-readable hash of a directory of files
    """
    result = hashlib.md5()
    last = None
    for dir, dirnames, pathnames in os.walk(path):
        for last in sorted(pathnames):
            current = '%s/%s' % (dir, last)
            data = open(current, 'rb').read()
            result.update(data)

    assert last, "Did not find any files to digest at %r" % path

    return humanize(result.hexdigest(), words=3)
