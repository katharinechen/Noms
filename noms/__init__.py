"""
Noms Python library - web application
"""
import re


DATABASE_NAME = "noms"


def urlify(*args):
    """
    Return a url-friendly version of name
    """
    args = list(args)

    for n in args:
        assert isinstance(n, unicode), "Arguments pass to urlify must be unicode"

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
    def realConfig(self):
        if '_realConfig' in self.__dict__:
            """
            We have already memoized previously
            """

        else:
            cfg = self.require()
            assert cfg is not None, "Couldn't load a config from the database"
            self.__dict__['_realConfig'] = cfg

        return self.__dict__['_realConfig']

    def __getattr__(self, attr):
        return getattr(self.realConfig, attr)

    def __hasattr__(self, attr):
        return hasattr(self.realConfig, attr)

    def __setattr__(self, attr, value):
        if self.realConfig:
            self.realConfig.__setattr__(attr, value)
        else:
            object.__setattr__(self, attr, value)

    @staticmethod
    def require():
        """
        => Config object, if any config has been saved in this db
        """
        from noms.config import Config
        return Config.objects().first()


CONFIG = LazyConfig()

