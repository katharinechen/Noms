"""
Noms Python library - web application
"""
import re

from codado import fromdir, enum

from pymongo.uri_parser import parse_uri


fromNoms = fromdir(__file__, '..')


DBHost = enum(
        noms={'host': 'mongodb://localhost/noms'},
        nomsTest={'host': 'mongomock://localhost/noms-test'},
        )

# mongomock is broken, we need to maintain our own connection aliases
# See https://github.com/vmalloc/mongomock/issues/233 - we must parse
# host ourselves and pass in db=, for the benefit of mongomock.
DBAlias = enum.fromkeys(DBHost.keys())


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
        assert isinstance(n, unicode), "Arguments passed to urlify must be unicode"

    url = args.pop(0)
    for n in args:
        url = url + "-" + n
    url = url.encode('punycode')

    return re.sub(r'[^-a-z0-9]', '-', url.lower())


class LazyConfig(object):
    """
    A placeholder for config that exists before the database is connected.

    This allows us to make CONFIG a simple global instance
    """
    @property
    def hasRealConfig(self):
        """
        => True if this object is initialized (previously memoized)
        """
        return '_realConfig' in self.__dict__

    @property
    def realConfig(self):
        """
        Lazily create a config for me to proxy
        """
        if not self.hasRealConfig:
            self.load()

        return self.__dict__['_realConfig']

    def __getattr__(self, attr):
        return getattr(self.realConfig, attr)

    def __setattr__(self, attr, value):
        if not self.hasRealConfig:
            raise TypeError('Cannot set values on uninitialized config')
        self.realConfig.__setattr__(attr, value)

    def load(self):
        """
        Initialize from the database
        """
        from noms.config import Config
        cfg = Config.objects().first()
        assert cfg is not None, "Couldn't load a config from the database"
        self.__dict__['_realConfig'] = cfg
        return self


CONFIG = LazyConfig()

