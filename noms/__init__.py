"""
Noms Python library - web application
"""
import os
from urllib.parse import quote_plus

from codado import fromdir, enum

from pymongo.uri_parser import parse_uri


fromNoms = fromdir(__file__, '..')


NOMS_DB_HOST = os.environ.get('NOMS_DB_HOST', 'localhost')


DBHost = enum(
        noms={'host': 'mongodb://%s/noms' % NOMS_DB_HOST},
        nomsTest={'host': 'mongomock://localhost/noms-test'},
        )

# mongomock is broken, we need to maintain our own connection aliases
# See https://github.com/vmalloc/mongomock/issues/233 - we must parse
# host ourselves and pass in db=, for the benefit of mongomock.
DBAlias = enum.fromkeys(list(DBHost.keys()))


def _parseHosts():
    """
    Build a dict of all of the connections defined by DBHost

    Doesn't register a default connection yet.
    """
    for k, v in DBHost.items():
        parts = parse_uri(v['host'].replace('mongomock', 'mongodb')) # hack for a parse_uri restriction
        DBHost[k]['db'] = parts['database']

_parseHosts()


def urlify(*args):
    """
    Return a url-friendly version of name
    """
    args = list(args)

    for n in args:
        assert not isinstance(n, bytes), "Arguments passed to urlify must be unicode"

    url = args.pop(0)
    for n in args:
        url = url + "-" + n
    url = url.encode('idna')

    return quote_plus(url)


class Config:
    """
    Config object using our Description class as the data.
    """
    def __getattr__(self, name):
        if not 'description' in self.__dict__:
            from noms.whisk.describe import Description
            self.description = Description.build()

        ret = getattr(self.__dict__['description'], name)[1]
        return ret


CONFIG = Config()
