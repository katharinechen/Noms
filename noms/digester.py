"""
Generate an md5 hash for a directory of files
"""
import os
import hashlib

from humanhash import humanize

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react
from twisted.python import util

import treq

from codado.tx import Main


class Options(Main):
    synopsis = "digester <directory>"

    optParameters = [
            ['update-url', 'U', None, 'Append the new hash to the URL and make an HTTP GET to update it'],
            ]

    def parseArgs(self, directory):
        self['directory'] = directory

    def postOptions(self):
        dig = digest(self['directory'])
        self._digest = dig
        print dig
        if self['update-url']:
            react(self.doUpdate)

    def doUpdate(self, reactor):
        """
        Make an HTTP GET to update-url with the new digest
        """
        url = self['update-url'] + self._digest
        return treq.get(url).addCallback(lambda r: util.println('update success'))


def digest(path):
    """
    Produce a human-readable hash of a directory of files
    """
    result = hashlib.md5()
    for dir, dirnames, pathnames in os.walk(path):
        for pn in pathnames:
            current = '%s/%s' % (dir, pn)
            data = open(current).read()
            result.update(data)

    return humanize(result.hexdigest(), words=3)
