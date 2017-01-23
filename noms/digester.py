"""
Generate an md5 hash for a directory of files
"""
import os
import hashlib

from humanhash import humanize

from codado.tx import Main



class Options(Main):
    synopsis = "digester <directory>"

    def parseArgs(self, directory):
        self['directory'] = directory

    def postOptions(self):
        result = hashlib.md5()
        for dir, dirnames, pathnames in os.walk(self['directory']):
            for pn in pathnames:
                current = '%s/%s' % (dir, pn)
                data = open(current).read()
                result.update(data)

        print humanize(result.hexdigest(), words=3)

