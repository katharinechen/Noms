"""
Noms Python library - web application
"""
import os
import re

from codado import fromdir


fromNoms = fromdir(__file__, '..')


NOMS_DB_HOST = os.environ.get('NOMS_DB_HOST', 'localhost')
DB_NAME = 'noms'
DB_CONNECT = f'mongodb://{NOMS_DB_HOST}/{DB_NAME}'


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

    return re.sub(rb'[^-a-z0-9]', b'-', url.lower()).decode('ascii')


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
