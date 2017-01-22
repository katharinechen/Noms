"""
Generate an md5 hash for a directory of files
"""
import sys, os
import hashlib

from humanhash import humanize

from twisted.python import usage


class Options(usage.Options):
    synopsis = " <directory>"

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

def run(argv=None):
    if argv is None:
        argv = sys.argv
    o = Options()
    try:
        o.parseOptions(argv[1:])
    except usage.UsageError, e:
        if hasattr(o, 'subOptions'):
            print str(o.subOptions)
        else:
            print str(o)
        print str(e)
        return 1

    return 0


if __name__ == '__main__': sys.exit(run())
